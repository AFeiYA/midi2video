"""Descending-layer hscroll planner.

The marble hits every note at its exact MIDI time. Between hits it is in free
flight under one constant gravity. Each plate is a passive frictionless
surface: restitution is at most 1, so a contact never increases kinetic
energy. Seeded noise only reorders candidates that already satisfy those
bounds.

Layers step downward. A gap at least ``long_note`` seconds long is the
ballistic arc onto the next lower layer. Inside a layer the seed picks a
compact fold, a compact forward run, or an upper/lower shuttle. A shuttle
rail stays below the previous layer. Nothing resets the course to the top.

If a note time cannot be met without adding energy or breaking a stated
constraint, the planner stops and writes an impossibility report. It does not
raise restitution above 1.
"""

import argparse
import json
import math
import sys

import numpy as np

from hscroll_descent.audit import audit_route
from hscroll_descent.clearance import flight_plate_gap, plate_plate_gap, sampled_flight_gap
from hscroll_descent.probes import (
    PAIR_MIN,
    SEARCH_KEEP,
    Placement,
    ProbeLibrary,
    keepout_against,
    obstacle_distance,
    pair_distance,
    sag_at,
    sag_samples,
)
from hscroll_descent.physics import (
    flight_apex_z,
    flight_state,
    gravity_vector,
    outgoing_grid,
    release_from_arrival,
    specific_energy,
)

MARBLE_RADIUS = 0.15
PLATE_RADIUS = 0.045
CONTACT_OFFSET = MARBLE_RADIUS + PLATE_RADIUS
ENTRY_VIN = (1.55, -4.50)
ENTRY_PRE = 0.42
LAYER_HALF_WIDTH = 1.55
LAYER_HARD_HALF = 5.5
POOL_LIMIT = 36
BACKTRACK_LIMIT = 600
CLEARANCE_MARGIN = 0.016
PLATE_MARGIN = 0.028


def add_args(ap):
    ap.add_argument("--long-note", type=float, default=0.60,
                    help="descent style: a gap at least this long (s) opens the next lower layer")
    ap.add_argument("--descent-max-drop", type=float, default=None,
                    help="descent style: optional maximum metres one layer arc may fall. "
                         "If passive flight cannot land that high, the run stops and reports the energy deficit. "
                         "v1's --max-drop is not read.")
    ap.add_argument("--plate-half", type=float, default=0.15,
                    help="descent style: half-length (m) of the capsule proxy for each contact plate")
    ap.add_argument("--patterns", default="",
                    help="descent style: comma list of fold,compact,shuttle for successive layers. "
                         "Empty = seeded draw.")
    ap.add_argument("--report", default="", help="descent style: also write the audit or impossibility JSON here")


def _as_patterns(text, n_layers, seed):
    if text:
        names = [part.strip() for part in text.split(",") if part.strip()]
        bad = [name for name in names if name not in ("fold", "compact", "shuttle")]
        if bad:
            raise SystemExit(f"unknown descent pattern {bad[0]!r} (fold, compact, shuttle)")
        return [names[i % len(names)] for i in range(n_layers)]
    rng = np.random.default_rng(seed)
    weights = np.array([0.46, 0.32, 0.22])
    return [str(rng.choice(["fold", "compact", "shuttle"], p=weights)) for _ in range(n_layers)]


def _segment(times, long_note):
    n = len(times)
    layer = [0] * n
    index_in = [0] * n
    long_launch = [False] * n
    for i in range(n - 1):
        if times[i + 1] - times[i] >= long_note:
            long_launch[i] = True
            layer[i + 1] = layer[i] + 1
        else:
            layer[i + 1] = layer[i]
            index_in[i + 1] = index_in[i] + 1
    return layer, index_in, long_launch


def _next_mount(i, n, layer, index_in, long_launch, pattern):
    if i >= n - 1:
        return None
    if layer[i + 1] != layer[i] or long_launch[i + 1] or i + 1 == n - 1:
        # The contact that opens a layer, launches a long arc, or ends the
        # excerpt is a floor hit. A ceiling launch cannot throw the long arc
        # upward, so it would fall much farther than a floor launch.
        return "floor"
    if pattern == "shuttle" and index_in[i + 1] % 2 == 1:
        return "ceil"
    return "floor"


def _target_dx(dt):
    # Strikers are about 0.67 m across. A short hop still aims past that width
    # when the speed budget can pay for it.
    return float(np.clip(2.4 * dt, 0.72, 1.35))


def _kinematic(i, spec, state):
    """Passive candidates for one pattern attempt. ``spec`` is (kind, pattern, adapted)."""
    kind, pattern, adapted = spec
    g = state["g"]
    pos = state["pos"][i]
    vin = state["vins"][i]
    mount = state["mounts"][i]
    dt = state["tail"] if i == state["n"] - 1 else state["times"][i + 1] - state["times"][i]
    grid = outgoing_grid(vin, mount, state["tilt"], state["restitutions"])
    layer_id = state["layer"][i]
    first = state["layer_first"][layer_id]
    anchor = state["pos"][first]
    open_z = float(anchor[1])
    prev_min = None if layer_id == 0 else min(float(state["pos"][j][1]) for j in range(i) if state["layer"][j] == layer_id - 1)
    layer_min = min(float(state["pos"][j][1]) for j in range(i + 1) if state["layer"][j] == layer_id)
    nxt = None if i == state["n"] - 1 else _next_mount(i, state["n"], state["layer"], state["index_in"], state["long_launch"], pattern)
    if state.get("lock_direction"):
        prefer = state.get("prefer0", 1.0)
    elif state["layer"][i] == 0:
        # The opening layer stays to the right. Folding back stacks the
        # strikers on top of each other before the long drop has a clear lane.
        prefer = 1.0
    else:
        prefer = 1.0 if state["index_in"][i] % 2 == 0 else -1.0
    upcoming_long = i + 1 < state["n"] and state["long_launch"][i + 1]
    out = []
    reasons = state.setdefault("last_reject", {})

    def reject(reason):
        reasons[reason] = reasons.get(reason, 0) + 1

    if not grid:
        reject("no_frictionless_bounce_on_this_mount")
    min_step = 0.20 if dt < 0.22 else 0.26
    fall_need = -0.25 if dt < 0.22 else -0.45
    for vout, normal, restitution, _approach in grid:
        if i == state["n"] - 1:
            end, _vend = flight_state(pos, vout, dt, g)
            dx = float(end[0] - pos[0])
            dz = float(end[1] - pos[1])
            apex = flight_apex_z(pos[1], vout[1], dt, g)
            if dx < 0.08 or end[1] > pos[1] - 0.02:
                reject("departure_shape")
                continue
            if apex > state["apex_cap"](layer_id, prev_min, pos[1]):
                reject("apex")
                continue
            score = 0.55 * (1.0 - restitution) + 0.25 * max(0.0, 0.9 - dx) + 0.15 * max(0.0, dz + 0.15)
            score += 0.40 * max(0.0, 1.15 - float(np.asarray(vout) @ np.asarray(normal)))
            out.append(dict(vout=vout, normal=normal, e=restitution, p1=None, v_next=None,
                            next_mount=None, dx=dx, dz=dz, kind="departure", pattern="departure",
                            adapted=False, score=score, dt=dt))
            continue
        p1, v_next = flight_state(pos, vout, dt, g)
        dx = float(p1[0] - pos[0])
        dz = float(p1[1] - pos[1])
        if float(p1[1]) > 1e-6:
            reject("above_start")
            continue
        if state.get("z_ceiling") is not None and float(p1[1]) > state["z_ceiling"] - 0.08:
            reject("reenters_previous_layer")
            continue
        apex = flight_apex_z(pos[1], vout[1], dt, g)
        if apex > state["apex_cap"](layer_id, prev_min, float(pos[1])):
            reject("apex")
            continue
        if nxt == "floor" and float(v_next[1]) > fall_need:
            reject("arrival_not_falling")
            continue
        if nxt == "ceil" and float(v_next[1]) < 0.35:
            reject("arrival_not_rising")
            continue
        if kind == "drop":
            if dx < 0.45 or dz > -0.50:
                reject("drop_shape")
                continue
            if float(p1[1]) > layer_min - 0.40:
                reject("drop_depth")
                continue
            if float(v_next[1]) > -0.55:
                reject("drop_arrival")
                continue
            if state["max_drop"] is not None and -dz > state["max_drop"] + 1e-9:
                reject("max_drop")
                continue
            score = abs(-dz - 2.05) + 0.28 * abs(dx - 1.75) + 0.35 * (1.0 - restitution)
            if -dz < 1.05:
                score += 1.5
        elif nxt == "ceil":
            rise = float(p1[1]) - open_z
            if not 0.26 <= rise <= 0.60:
                reject("shuttle_rise")
                continue
            if prev_min is not None and (float(p1[1]) > prev_min - 0.30):
                reject("shuttle_reenters_previous_layer")
                continue
            half_limit = 3.3 if layer_id == 0 else LAYER_HARD_HALF
            if abs(float(p1[0]) - float(anchor[0])) > half_limit:
                reject("outside_layer")
                continue
            if abs(dx) < min_step:
                reject("too_close")
                continue
            score = abs(rise - 0.42) + 0.35 * abs(abs(dx) - _target_dx(dt)) + 1.40 * (1.0 - restitution)
            over = abs(float(p1[0]) - float(anchor[0])) - LAYER_HALF_WIDTH
            if over > 0.0:
                score += 0.85 * over
        else:
            half_limit = 3.3 if layer_id == 0 else LAYER_HARD_HALF
            if abs(float(p1[0]) - float(anchor[0])) > half_limit:
                reject("outside_layer")
                continue
            if float(p1[1]) < open_z - 1.80 or float(p1[1]) > min(0.0, open_z + 0.25):
                reject("layer_band")
                continue
            if abs(dx) < min_step:
                reject("floor_step")
                continue
            # High restitution keeps the energy that descent converts into speed.
            # A flat step with a low restitution is legal but it cannot feed a long arc.
            score = 1.70 * (1.0 - restitution)
            score += 0.45 * abs(dz + 0.22) + 0.22 * abs(abs(dx) - _target_dx(dt))
            score += 0.55 * max(0.0, dz + 0.02)
            over = abs(float(p1[0]) - float(anchor[0])) - LAYER_HALF_WIDTH
            if over > 0.0:
                score += 0.85 * over
            if kind == "fold" and not upcoming_long and dx * prefer < 0.0:
                score += 0.70
            if upcoming_long and float(vin[0]) * dx < 0.0:
                score += 0.45
        if upcoming_long:
            speed_next = float(np.linalg.norm(v_next))
            score += 0.50 * max(0.0, 5.0 - speed_next)
        if adapted:
            score += 1.35
        # Real strikers are wider than the capsule. Prefer a step that can
        # separate them, and a departure with enough normal speed to leave the
        # body before the 1.2-frame strike window closes.
        score += 2.40 * max(0.0, 0.78 - abs(dx))
        score += 0.40 * max(0.0, 1.15 - float(np.asarray(vout) @ np.asarray(normal)))
        out.append(dict(vout=np.array(vout), normal=np.array(normal), e=float(restitution),
                        p1=np.array(p1), v_next=np.array(v_next), next_mount=nxt,
                        dx=dx, dz=dz, kind=kind, pattern=pattern, adapted=adapted,
                        score=float(score), dt=float(dt)))
    return out


def _rank(cands, seed, i):
    """Seeded reorder. The noise does not create candidates or add speed."""
    if not cands:
        return []
    rng = np.random.default_rng([int(seed) & 0x7FFFFFFF, int(i), 17])
    jitter = rng.normal(0.0, 0.045, size=len(cands))
    ranked = []
    for cand, noise in zip(cands, jitter):
        cand["score"] = float(cand["score"] + noise)
        ranked.append(cand)
    ranked.sort(key=lambda cand: cand["score"])
    return ranked


def _plate(center_contact, normal, half):
    normal = np.asarray(normal, dtype=float)
    center = np.asarray(center_contact, dtype=float) - normal * CONTACT_OFFSET
    return dict(center=center, normal=normal, half_length=float(half), radius=PLATE_RADIUS)


def _gap_ok(p0, velocity, dt, plate, g, ignore_start=0.0, ignore_end=0.0, limit=CLEARANCE_MARGIN):
    # Search uses dense samples. The independent audit repeats the gap at the
    # polynomial critical points, so a sampled near-miss still fails the test.
    fast = sampled_flight_gap(p0, velocity, dt, g, plate, MARBLE_RADIUS, samples=72,
                              ignore_start=ignore_start, ignore_end=ignore_end)
    return fast >= limit


def _own_plate_ok(p0, velocity, dt, plate, g, ignore_start=0.0, ignore_end=0.0):
    """A flight may touch its own plate at the contact and nowhere else."""
    fast = sampled_flight_gap(p0, velocity, dt, g, plate, MARBLE_RADIUS, samples=72,
                              ignore_start=ignore_start, ignore_end=ignore_end)
    return fast >= -1e-4


def _pinned_at(state, t):
    pins = state.get("pinned_frames") or {}
    row = pins.get(round(float(t), 6))
    if row is None:
        return None
    return np.asarray(row, dtype=float)


def _pos_at(state, t, cand=None, index=None):
    """Marble centre at a frame time, including a candidate that is not applied yet."""
    pinned = _pinned_at(state, t)
    if pinned is not None and (index is None or t < state["times"][index] - 1e-9):
        return pinned
    if cand is not None and index is not None and t >= state["times"][index] - 1e-12:
        point, _vel = flight_state(state["pos"][index], cand["vout"], t - state["times"][index], state["g"])
        return np.asarray(point, dtype=float)
    chosen = state["flights"][0]
    for flight in state["flights"]:
        if flight["t0"] <= t + 1e-12:
            chosen = flight
        else:
            break
    point, _vel = flight_state(chosen["p0"], chosen["v"], max(0.0, t - chosen["t0"]), state["g"])
    return np.asarray(point, dtype=float)


def _visual_origin(state, index, cand):
    """Plate origin that puts the contact on the sagged path at the MIDI onset."""
    t = float(state["times"][index])
    fps = float(state["fps"])
    g = float(state["g"])
    f0 = math.floor(t * fps + 1e-9)
    u = t * fps - f0
    p0 = _pos_at(state, f0 / fps, cand, index)
    if u < 1e-8:
        centre = p0
    else:
        p1 = _pos_at(state, (f0 + 1) / fps, cand, index)
        centre = np.array([
            p0[0] * (1.0 - u) + p1[0] * u,
            p0[1] * (1.0 - u) + p1[1] * u + 0.5 * g * (u / fps) * ((1.0 - u) / fps),
        ])
    normal = np.asarray(cand["normal"], dtype=float)
    return centre - normal * CONTACT_OFFSET, centre


def _frames_through(state, index, cand):
    t_end = float(state["times"][index] + cand["dt"])
    fps = float(state["fps"])
    t0 = float(state["flights"][0]["t0"])
    # A resumed route has no frames before the guide landing. Extrapolating
    # the 1 ms lead back to t=0 would invent a path the marble never flies.
    first = 0 if t0 <= 0.0 else int(math.floor(t0 * fps + 1e-9))
    last = int(math.floor(t_end * fps + 1e-9))
    last = max(last, first)
    rows = [_pos_at(state, k / fps, cand, index) for k in range(first, last + 1)]
    return np.asarray(rows, dtype=float), first


def _samples_from_frames(frames, first_index, fps, g, sub=8):
    """Sag samples whose frame 0 is ``first_index``, not necessarily t=0."""
    if len(frames) < 2:
        return np.zeros((0, 3)), np.zeros(0)
    fps = float(fps)
    step = 1.0 / (fps * sub)
    t0 = first_index / fps
    t1 = (first_index + len(frames) - 1) / fps
    ts = np.arange(t0, t1, step)
    local = ts * fps - first_index
    f0 = np.floor(local + 1e-12).astype(int)
    u = local - f0
    f1 = np.minimum(f0 + 1, len(frames) - 1)
    x = frames[f0, 0] * (1.0 - u) + frames[f1, 0] * u
    z = frames[f0, 1] * (1.0 - u) + frames[f1, 1] * u + 0.5 * float(g) * (u / fps) * ((1.0 - u) / fps)
    return np.c_[x, np.zeros(len(ts)), z], ts


def _probe_clear(i, cand, state):
    """Full y-slab keep-out and stride-2 pair gap. Capsules are not enough."""
    library = state.get("probe_lib")
    if library is None:
        return True
    fails = state.setdefault("clear_fail", {})
    hop_fails = state.setdefault("hop_fail", {})
    name, variant, _j = state["assets"][i]
    origin, _centre = _visual_origin(state, i, cand)
    normal = cand["normal"]
    margins = []
    for other in state["placed"]:
        gap = pair_distance(library, name, variant, origin, normal, other)
        if gap < PAIR_MIN:
            fails["probe_pair"] = fails.get("probe_pair", 0) + 1
            hop_fails["probe_pair"] = hop_fails.get("probe_pair", 0) + 1
            return False
        margins.append(gap)
    for cloud in state.get("obstacle_clouds") or []:
        gap = obstacle_distance(cloud, origin, normal, library, name, variant)
        if gap is not None and gap < PAIR_MIN:
            fails["probe_rail"] = fails.get("probe_rail", 0) + 1
            return False
        if gap is not None:
            margins.append(gap)
    frames, first_index = _frames_through(state, i, cand)
    samples, times = _samples_from_frames(frames, first_index, state["fps"], state["g"], sub=8)
    extra_s = state.get("extra_samples")
    extra_t = state.get("extra_times")
    if extra_s is not None and len(extra_s):
        samples = np.vstack([samples, extra_s]) if len(samples) else extra_s
        times = np.concatenate([times, extra_t]) if len(times) else extra_t
    own = Placement(library, name, variant, origin, normal, state["times"][i])
    ok, dist = keepout_against(own, samples, times, state["fps"], SEARCH_KEEP)
    if not ok:
        fails["probe_own"] = fails.get("probe_own", 0) + 1
        hop_fails["probe_own"] = hop_fails.get("probe_own", 0) + 1
        if dist is not None:
            state["own_dist"] = float(dist)
        return False
    if dist is not None:
        margins.append(dist)
    for other in state["placed"]:
        ok, dist = keepout_against(other, samples, times, state["fps"], SEARCH_KEEP)
        if not ok:
            fails["probe_path"] = fails.get("probe_path", 0) + 1
            hop_fails["probe_path"] = hop_fails.get("probe_path", 0) + 1
            return False
        if dist is not None:
            margins.append(dist)
    cand["visual_origin"] = np.asarray(origin, dtype=float)
    cand["probe_margin"] = min(margins) if margins else 1.0
    if i + 1 < state["n"] - 1 and state["long_launch"][i + 1] and cand.get("v_next") is not None:
        dt_drop = float(state["times"][i + 2] - state["times"][i + 1])
        layer_id = state["layer"][i + 1]
        lows = [float(state["pos"][j][1]) for j in range(i + 1) if state["layer"][j] == layer_id]
        lows.append(float(cand["p1"][1]))
        own_plate = _plate(state["pos"][i], cand["normal"], state["plate_half"])
        if not _can_drop(cand["v_next"], dt_drop, state["g"], state["tilt"], float(cand["p1"][1]), min(lows), state, cand["p1"], [own_plate]):
            fails["drop_feed"] = fails.get("drop_feed", 0) + 1
            hop_fails["drop_feed"] = hop_fails.get("drop_feed", 0) + 1
            return False
    if not _has_short_escape(state, i, cand, own):
        fails["probe_escape"] = fails.get("probe_escape", 0) + 1
        hop_fails["probe_escape"] = hop_fails.get("probe_escape", 0) + 1
        return False
    return True


def _has_short_escape(state, i, cand, own):
    """A landing that leaves no legal strike on a very short next note is a dead end.

    The note after this flight is short enough that the marble is still inside
    a glockenspiel unless the arrival can leave along the plate normal. Reject
    the landing when no passive bounce does that.
    """
    if cand.get("p1") is None or i + 2 >= state["n"]:
        return True
    dt = float(state["times"][i + 2] - state["times"][i + 1])
    if dt >= 0.22:
        return True
    library = state.get("probe_lib")
    if library is None:
        return True
    pos = np.asarray(cand["p1"], dtype=float)
    vin = np.asarray(cand["v_next"], dtype=float)
    mount = cand.get("next_mount") or "floor"
    name, variant, _j = state["assets"][i + 1]
    g = state["g"]
    hit_time = float(state["times"][i + 1])
    grid = outgoing_grid(vin, mount, state["tilt"], np.array([0.85, 1.0]))
    neighbors = list(state["placed"]) + [own]
    fps = float(state["fps"])
    tried = 0
    for vout, normal, _e, _approach in grid:
        if tried >= 36:
            break
        tried += 1
        p1, v_next = flight_state(pos, vout, dt, g)
        if mount == "floor" and float(v_next[1]) > -0.20:
            continue
        if abs(float(p1[0] - pos[0])) < 0.18:
            continue
        origin = pos - np.asarray(normal, dtype=float) * CONTACT_OFFSET
        if any(pair_distance(library, name, variant, origin, normal, other) < PAIR_MIN for other in neighbors):
            continue
        item = Placement(library, name, variant, origin, normal, hit_time)
        samples = []
        times = []
        for step in range(1, 8):
            t = dt * step / 7.0
            if t < 1.2 / fps:
                continue
            point, _vel = flight_state(pos, vout, t, g)
            samples.append([point[0], 0.0, point[1]])
            times.append(hit_time + t)
        if not samples:
            continue
        samples = np.asarray(samples, dtype=float)
        times = np.asarray(times, dtype=float)
        ok, _dist = keepout_against(item, samples, times, fps, SEARCH_KEEP)
        if not ok:
            continue
        if any(not keepout_against(other, samples, times, fps, SEARCH_KEEP)[0] for other in neighbors):
            continue
        if i + 3 < state["n"]:
            dt_drop = float(state["times"][i + 3] - state["times"][i + 2])
            if dt_drop >= state["long_note"] and not _can_drop(v_next, dt_drop, g, state["tilt"], float(p1[1]), float(p1[1]) - 0.40):
                continue
        return True
    return False


def _can_drop(vin, dt, g, tilt, z0, layer_min, state=None, pos=None, also=None):
    """True when some passive bounce can open the next layer and its plate fits."""
    others = []
    if state is not None:
        others.extend(state["plates"])
    if also:
        others.extend(also)
    for vout, normal, _e, _approach in outgoing_grid(vin, "floor", tilt, np.array([0.85, 1.0])):
        end, v_next = flight_state(np.array([0.0, z0]), vout, dt, g)
        dx = float(end[0])
        dz = float(end[1] - z0)
        if dx < 0.45 or dz > -0.50 or float(v_next[1]) > -0.55:
            continue
        if float(end[1]) > layer_min - 0.40:
            continue
        if pos is not None and others:
            plate = _plate(pos, normal, state["plate_half"])
            blocked = False
            for other in others:
                if plate_plate_gap(plate, other, PLATE_RADIUS) < PLATE_MARGIN:
                    blocked = True
                    break
                if not _gap_ok(pos, vout, dt, other, g):
                    blocked = True
                    break
            if blocked:
                continue
        return True
    return False


def _clear(i, cand, state):
    g = state["g"]
    pos = state["pos"][i]
    plate = _plate(pos, cand["normal"], state["plate_half"])
    fails = state.setdefault("clear_fail", {})
    for other in state["plates"]:
        if plate_plate_gap(plate, other, PLATE_RADIUS) < PLATE_MARGIN:
            fails["pair"] = fails.get("pair", 0) + 1
            state.setdefault("hop_fail", {})["pair"] = state["hop_fail"].get("pair", 0) + 1
            return False
    outgoing_dt = cand["dt"]
    for other in state["plates"]:
        if not _gap_ok(pos, cand["vout"], outgoing_dt, other, g):
            fails["path"] = fails.get("path", 0) + 1
            state.setdefault("hop_fail", {})["path"] = state["hop_fail"].get("path", 0) + 1
            return False
    if not _own_plate_ok(pos, cand["vout"], outgoing_dt, plate, g, ignore_start=1.2 / state["fps"]):
        fails["own"] = fails.get("own", 0) + 1
        state.setdefault("hop_fail", {})["own"] = state["hop_fail"].get("own", 0) + 1
        return False
    incoming = state["incoming"](i)
    if not _own_plate_ok(incoming["p0"], incoming["v"], incoming["t1"] - incoming["t0"], plate, g,
                         ignore_end=1.2 / state["fps"]):
        fails["incoming"] = fails.get("incoming", 0) + 1
        return False
    # Later plates must not be built on top of the path already flown.
    for flight in state["flights"]:
        if flight.get("end_contact") == i or flight.get("start_contact") == i:
            continue
        if not _gap_ok(flight["p0"], flight["v"], flight["t1"] - flight["t0"], plate, g):
            fails["history"] = fails.get("history", 0) + 1
            state.setdefault("hop_fail", {})["history"] = state["hop_fail"].get("history", 0) + 1
            return False
    # Polynomial critical points. Samples can miss a minimum between them.
    gvec = gravity_vector(g)
    for other in state["plates"]:
        gap = flight_plate_gap(pos, cand["vout"], outgoing_dt, gvec, other, MARBLE_RADIUS)
        if gap < CLEARANCE_MARGIN:
            fails["poly_path"] = fails.get("poly_path", 0) + 1
            return False
    for flight in state["flights"]:
        if flight.get("end_contact") == i or flight.get("start_contact") == i:
            continue
        gap = flight_plate_gap(flight["p0"], flight["v"], flight["t1"] - flight["t0"], gvec, plate, MARBLE_RADIUS)
        if gap < CLEARANCE_MARGIN:
            fails["poly_history"] = fails.get("poly_history", 0) + 1
            return False
    for extra in state.get("extra_plates") or []:
        if not _gap_ok(pos, cand["vout"], outgoing_dt, extra, g):
            fails["guide"] = fails.get("guide", 0) + 1
            return False
        for flight in state["flights"]:
            if flight.get("role") == "resume":
                continue
            if not _gap_ok(flight["p0"], flight["v"], flight["t1"] - flight["t0"], extra, g):
                fails["guide"] = fails.get("guide", 0) + 1
                return False
    own_gap = flight_plate_gap(pos, cand["vout"], outgoing_dt, gvec, plate, MARBLE_RADIUS)
    in_gap = flight_plate_gap(incoming["p0"], incoming["v"], incoming["t1"] - incoming["t0"], gvec, plate, MARBLE_RADIUS)
    if own_gap < -2e-5 or in_gap < -2e-5:
        fails["poly_own"] = fails.get("poly_own", 0) + 1
        return False
    return _probe_clear(i, cand, state)


def _shallowest_drop(vin, pos, dt, g, tilt, restitutions):
    best = None
    for vout, _normal, _e, _a in outgoing_grid(vin, "floor", tilt, restitutions):
        p1, v_next = flight_state(pos, vout, dt, g)
        dx = float(p1[0] - pos[0])
        drop = float(pos[1] - p1[1])
        if dx < 0.30 or float(v_next[1]) > -0.30:
            continue
        if best is None or drop < best:
            best = drop
    return best


def _impossible(i, state, blocker, searched):
    g = state["g"]
    vin = np.asarray(state["vins"][i], dtype=float)
    pos = np.asarray(state["pos"][i], dtype=float)
    dt = None if i >= state["n"] - 1 else float(state["times"][i + 1] - state["times"][i])
    preferred = None
    deficit = None
    required_speed = None
    shallow = None
    if dt is not None and state["long_launch"][i]:
        drop = 2.0 if state["max_drop"] is None else min(2.0, state["max_drop"])
        v_need = np.array([1.60 / dt, (-drop + 0.5 * g * dt * dt) / dt])
        required_speed = float(np.linalg.norm(v_need))
        deficit = 0.5 * (float(v_need @ v_need) - float(vin @ vin))
        preferred = drop
        if state["mounts"][i] == "floor":
            shallow = _shallowest_drop(vin, pos, dt, g, state["tilt"], state["restitutions"])
    elif dt is not None:
        step = _target_dx(dt)
        v_need = np.array([step / dt, (-0.10 + 0.5 * g * dt * dt) / dt])
        required_speed = float(np.linalg.norm(v_need))
        deficit = 0.5 * (float(v_need @ v_need) - float(vin @ vin))
        preferred = 0.10
    tradeoffs = [
        "Keep restitution at or below 1. A plate in this template does not add speed.",
        "If the shallowest passive drop is deeper than the picture you wanted, use that deeper arc. Raising the landing would require energy the contact does not have.",
        "A higher or faster entry changes the energy budget before the first contact. It is not a collision gain. It also changes every later hop.",
        "Shorten this MIDI gap, or leave the marble lower and faster on the previous hop, if the landing must be higher. This planner does not move note times.",
        "hscroll v2 is a separate template. Its strikers are powered and may speed the marble up. That is not a passive reading of this route.",
    ]
    if deficit is not None and deficit <= 1e-9:
        tradeoffs.insert(0, "The preferred landing is inside the speed budget. The miss is geometric or a clearance miss, not a missing joule. Do not add speed to skip the collision.")
    if blocker == "clearance":
        tradeoffs.insert(0, "The passive landings that meet the clock collide with a plate proxy. Widen the layer or shorten the proxy plate. That is a geometry change, not permission to add energy.")
    if state["max_drop"] is not None and shallow is not None and shallow > state["max_drop"]:
        tradeoffs.insert(0, f"The shallowest rightward passive drop from this contact is {shallow:.2f} m, deeper than --descent-max-drop {state['max_drop']:.2f} m. Drop the cap, or change the entry or the MIDI. Do not add the missing speed at the plate.")
    return dict(
        status="impossible",
        hit=int(i),
        time=float(state["times"][i]),
        dt=dt,
        mount=state["mounts"][i],
        incoming_velocity=[float(vin[0]), float(vin[1])],
        incoming_speed=float(np.linalg.norm(vin)),
        energy_in_j_per_kg=specific_energy(vin, pos[1], g),
        blocker=blocker,
        reject_counts=state.get("last_reject", {}),
        clear_fail=dict(state.get("clear_fail", {})),
        hop_fail=dict(state.get("hop_fail") or {}),
        hop_fail_at=state.get("hop_fail_at"),
        debug_vin=state.get("debug_vin"),
        kinematic_ok=state.get("kinematic_ok"),
        own_dist=state.get("own_dist"),
        debug_plates=[
            dict(c=[float(p["center"][0]), float(p["center"][1])], n=[float(p["normal"][0]), float(p["normal"][1])])
            for p in state["plates"]
        ],
        position=[float(pos[0]), float(pos[1])],
        layer=int(state["layer"][i]),
        pattern=state["patterns"][state["layer"][i]],
        searched_candidates=int(searched),
        pool_sizes=list(state.get("pool_sizes") or []),
        backtracks=int(state["backtracks"]),
        shallowest_passive_drop_m=None if shallow is None else float(shallow),
        preferred_drop_m=preferred,
        required_outgoing_speed_m_s=required_speed,
        energy_deficit_j_per_kg=None if deficit is None else float(deficit),
        preferred_inside_speed_budget=bool(deficit is not None and deficit <= 1e-9),
        energy_was_relaxed=False,
        tradeoffs=tradeoffs,
        message="Exact MIDI timing has no passive frictionless placement inside the stated bounds. Energy was not increased.",
    )


def _search(state):
    n = state["n"]
    pools = [None] * n
    cursors = [0] * n
    i = 0
    while i < n:
        if pools[i] is None:
            state["last_reject"] = {}
            state["hop_fail"] = {}
            state["hop_fail_at"] = i
            if i < len(state["vins"]):
                state["debug_vin"] = [float(state["vins"][i][0]), float(state["vins"][i][1]), float(state["pos"][i][1])]
            pattern = state["patterns"][state["layer"][i]]
            if i == n - 1:
                groups = [("departure", "departure", False)]
            elif state["long_launch"][i]:
                groups = [("drop", "drop", False)]
            else:
                groups = [(pattern, pattern, False)]
                if pattern != "fold":
                    groups.append(("fold", "fold", True))
                # A fold that reverses into a striker it just left cannot clear
                # the real mesh. Compact (keep going) is the adapted alternative.
                if pattern != "compact":
                    groups.append(("compact", "compact", True))
            found = []
            for spec in groups:
                found.extend(_kinematic(i, spec, state))
            ranked = _rank(found, state["seed"], i)
            # Keep both directions near the front on intra-layer hops so a fold
            # is not trimmed away before clearance is known.
            if groups[0][0] not in ("drop", "departure"):
                sign = state.get("prefer0", 1.0) if state.get("lock_direction") else 1.0
                primary = [cand for cand in ranked if cand["dx"] * sign >= 0.0][:90]
                other = [cand for cand in ranked if cand["dx"] * sign < 0.0][:30]
                seen = set()
                mixed = []
                for cand in primary + other:
                    if id(cand) in seen:
                        continue
                    seen.add(id(cand))
                    mixed.append(cand)
                ranked = mixed + [cand for cand in ranked if id(cand) not in seen]
            state["kinematic_ok"] = len(ranked)
            cleared = []
            for cand in ranked[:500]:
                if _clear(i, cand, state):
                    cleared.append(cand)
                    if len(cleared) >= 10:
                        break
            sign = state.get("prefer0", 1.0) if state.get("lock_direction") else 1.0
            if i <= 3 and not state.get("lock_direction") and cleared and cleared[0].get("p1") is not None:
                # The opening run goes out in front so the first long drop
                # falls beside the strikers. Later hops prefer a real gap.
                cleared.sort(key=lambda cand: (-float(cand["p1"][0]), -cand.get("probe_margin", 0.0)))
            else:
                cleared.sort(key=lambda cand: -cand.get("probe_margin", 0.0))
            forward = [cand for cand in cleared if cand.get("dx", sign) * sign >= 0.0][:3]
            backward = [] if not state.get("lock_direction") else [cand for cand in cleared if cand.get("dx", sign) * sign < 0.0][:2]
            picked = []
            seen = set()
            for cand in forward + backward + cleared:
                if id(cand) in seen:
                    continue
                seen.add(id(cand))
                picked.append(cand)
                if len(picked) == 4:
                    break
            pools[i] = picked
            cursors[i] = 0
            state["pool_sizes"][i] = len(pools[i])
        if cursors[i] >= len(pools[i]):
            blocker = "clearance" if state.get("kinematic_ok", 0) else "no_passive_candidate"
            if i == 0 or state["backtracks"] >= BACKTRACK_LIMIT:
                return _impossible(i, state, blocker, state["pool_sizes"][i])
            _undo(state)
            pools[i] = None
            i -= 1
            cursors[i] += 1
            state["backtracks"] += 1
            continue
        cand = pools[i][cursors[i]]
        if not _clear(i, cand, state):
            cursors[i] += 1
            continue
        _apply(i, cand, state)
        i += 1
    return None


def _incoming(state, i):
    if i == 0:
        return state["lead"]
    return state["flights"][-1]


def _apply(i, cand, state):
    pos = np.array(state["pos"][i], copy=True)
    normal = np.array(cand["normal"], copy=True)
    plate = _plate(pos, normal, state["plate_half"])
    plate["contact"] = i
    state["plates"].append(plate)
    if state.get("probe_lib") is not None:
        origin = cand.get("visual_origin")
        if origin is None:
            origin, _centre = _visual_origin(state, i, cand)
        name, variant, _j = state["assets"][i]
        state["placed"].append(Placement(
            state["probe_lib"], name, variant, origin, normal, state["times"][i],
        ))
    contact = dict(
        i=i, time=float(state["times"][i]), p=[float(pos[0]), float(pos[1])],
        vin=[float(state["vins"][i][0]), float(state["vins"][i][1])],
        vout=[float(cand["vout"][0]), float(cand["vout"][1])],
        normal=[float(normal[0]), float(normal[1])], restitution=float(cand["e"]),
        mount=state["mounts"][i], layer=int(state["layer"][i]),
        pattern=cand["pattern"], pattern_adapted=bool(cand["adapted"]),
        kind=cand["kind"], plate_center=[float(plate["center"][0]), float(plate["center"][1])],
        half_length=float(state["plate_half"]),
    )
    state["contacts"].append(contact)
    flight = dict(
        role="departure" if i == state["n"] - 1 else "hop",
        t0=float(state["times"][i]),
        t1=float(state["times"][i] + cand["dt"]),
        p0=[float(pos[0]), float(pos[1])],
        v=[float(cand["vout"][0]), float(cand["vout"][1])],
        start_contact=i,
        end_contact=None if i == state["n"] - 1 else i + 1,
    )
    state["flights"].append(flight)
    if i < state["n"] - 1:
        state["pos"].append(np.array(cand["p1"], copy=True))
        state["vins"].append(np.array(cand["v_next"], copy=True))
        state["mounts"].append(cand["next_mount"])


def _undo(state):
    state["plates"].pop()
    if state.get("placed"):
        state["placed"].pop()
    state["contacts"].pop()
    flight = state["flights"].pop()
    if flight["end_contact"] is not None:
        state["pos"].pop()
        state["vins"].pop()
        state["mounts"].pop()


def plan_hits(hits, g=9.81, seed=4, fps=30, tilt_deg=60.0, long_note=0.60, max_drop=None,
              plate_half=0.15, patterns="", entry_vin=None, entry_pre=ENTRY_PRE, duration=None,
              scope="excerpt", resume=None, extra_plates=None):
    """Plan one marble. Returns a route dict with status 'ok' or 'impossible'.

    ``resume`` continues after a guide. It is the arrival state at the first
    hit: ``p``, ``v``, and optional ``z_ceiling`` (the previous layer must stay
    above later contacts). There is no fresh drop from rest.
    """
    if len(hits) < 1:
        raise ValueError("descent planner needs at least one hit")
    times = [float(h["time"]) for h in hits]
    if any(b <= a for a, b in zip(times, times[1:])):
        return dict(status="impossible", hit=0, time=times[0], blocker="non_increasing_times",
                    energy_was_relaxed=False, message="Hit times must be strictly increasing.",
                    tradeoffs=["Fix the hit extraction. The planner does not reorder notes or add energy."])
    g = float(g)
    n = len(times)
    if duration is None:
        duration = times[-1] + 0.55
    duration = float(duration)
    if duration < times[-1] + 0.40:
        duration = times[-1] + 0.50
    layer, index_in, long_launch = _segment(times, long_note)
    n_layers = layer[-1] + 1
    pattern_of = _as_patterns(patterns, n_layers, seed)
    layer_first = [layer.index(level) for level in range(n_layers)]
    if resume is None:
        vin0 = np.array(ENTRY_VIN if entry_vin is None else entry_vin, dtype=float)
        if vin0[1] >= -0.30:
            raise ValueError("entry arrival must be falling (vin_z < -0.30) so the first plate is a floor")
        p0 = np.zeros(2)
        release_p, release_v = release_from_arrival(p0, vin0, entry_pre, g)
        lead = dict(role="lead_in", t0=float(-entry_pre), t1=0.0,
                    p0=[float(release_p[0]), float(release_p[1])],
                    v=[float(release_v[0]), float(release_v[1])],
                    start_contact=None, end_contact=0)
        z_ceiling = None
        prefer0 = 1.0
        lock_direction = False
    else:
        p0 = np.array(resume["p"], dtype=float)
        vin0 = np.array(resume["v"], dtype=float)
        if vin0[1] >= -0.05:
            return dict(status="impossible", hit=0, time=times[0], blocker="resume_not_falling",
                        energy_was_relaxed=False,
                        message="The guide landing is not falling onto the next note. Exit speed was not increased.")
        eps = 1e-3
        accel = np.array([0.0, -g])
        v_start = vin0 - accel * eps
        p_start = p0 - v_start * eps - 0.5 * accel * eps * eps
        lead = dict(role="resume", t0=float(times[0] - eps), t1=float(times[0]),
                    p0=[float(p_start[0]), float(p_start[1])],
                    v=[float(v_start[0]), float(v_start[1])],
                    start_contact=None, end_contact=0)
        z_ceiling = resume.get("z_ceiling")
        entry_pre = 0.0
        prefer0 = 1.0 if vin0[0] >= 0 else -1.0
        lock_direction = True
    state = dict(
        g=g, n=n, times=times, seed=seed, tilt=float(tilt_deg), max_drop=max_drop,
        plate_half=float(plate_half), layer=layer, index_in=index_in, long_launch=long_launch,
        patterns=pattern_of, restitutions=np.linspace(0.08, 1.0, 24), layer_first=layer_first,
        pos=[p0.copy()], vins=[vin0.copy()], mounts=["floor" if vin0[1] < 0 else "ceil"],
        plates=[], contacts=[], flights=[lead], lead=lead, backtracks=0, pool_sizes=[0] * n,
        tail=duration - times[-1], z_ceiling=z_ceiling, extra_plates=extra_plates or [],
        prefer0=prefer0, lock_direction=lock_direction, fps=int(fps),
        long_note=float(long_note),
    )
    probe_lib = ProbeLibrary("v5")
    state["probe_lib"] = probe_lib
    state["assets"] = probe_lib.assign(hits)
    state["placed"] = []
    pins = {}
    for row in (resume or {}).get("pinned_frames") or []:
        pins[round(float(row[0]), 6)] = [float(row[1]), float(row[2])]
    state["pinned_frames"] = pins
    extra = (resume or {}).get("extra_path")
    if extra:
        extra = np.asarray(extra, dtype=float)
        state["extra_times"] = extra[:, 0]
        state["extra_samples"] = np.c_[extra[:, 1], np.zeros(len(extra)), extra[:, 2]]
    else:
        state["extra_times"] = None
        state["extra_samples"] = None
    state["obstacle_clouds"] = list((resume or {}).get("obstacle_clouds") or [])
    state["incoming"] = lambda i: _incoming(state, i)

    def apex_cap(layer_id, prev_min, takeoff_z):
        # A passive lob may rise above its takeoff. It may not climb back into
        # a layer the marble has already left, and the opening lob stays bounded.
        if layer_id == 0 and state.get("z_ceiling") is not None:
            return state["z_ceiling"] - 0.10
        if layer_id == 0 or prev_min is None:
            return max(takeoff_z, 0.0) + 1.60
        return prev_min - 0.10

    state["apex_cap"] = apex_cap
    failed = _search(state)
    if failed is not None:
        failed.update(scope=scope, gravity=g, seed=int(seed), long_note=float(long_note),
                      patterns=pattern_of, energy_injection_allowed=False)
        return failed
    hits_out = [dict(time=float(h["time"]), note=h.get("note"), track=h.get("track_name", h.get("track", "")),
                     drum=bool(h.get("drum", False)), program=h.get("program")) for h in hits]
    route = dict(
        status="ok", g=g, seed=int(seed), fps=int(fps), duration=duration, scope=scope,
        long_note=float(long_note), tilt_deg=float(tilt_deg), max_drop=max_drop,
        plate_half=float(plate_half), plate_radius=PLATE_RADIUS, marble_radius=MARBLE_RADIUS,
        patterns=pattern_of, layers=layer, contacts=state["contacts"], flights=state["flights"],
        plates=[{k: (v if not isinstance(v, np.ndarray) else v.tolist()) for k, v in plate.items()} for plate in state["plates"]],
        hits=hits_out, backtracks=int(state["backtracks"]),
        entry=dict(pre_s=float(entry_pre), release_p=lead["p0"], release_v=lead["v"],
                   arrival_v=[float(vin0[0]), float(vin0[1])],
                   energy_j_per_kg=specific_energy(vin0, float(p0[1]), g),
                   resumed=resume is not None),
    )
    report = audit_route(route)
    route["audit"] = report
    if not report["ok"]:
        return dict(status="audit_failed", energy_was_relaxed=False, scope=scope, gravity=g, seed=int(seed),
                    violations=report["violations"], summary=report["summary"],
                    message="A candidate was assembled but the independent proxy audit rejected it. Energy was not relaxed to force a pass.")
    return route


def _smooth(values, fps, sigma_s):
    sigma = max(float(fps) * float(sigma_s), 1.0)
    radius = int(3 * sigma)
    kernel_x = np.arange(-radius, radius + 1)
    kernel = np.exp(-0.5 * (kernel_x / sigma) ** 2)
    kernel /= kernel.sum()
    padded = np.pad(np.asarray(values, dtype=float), radius, mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def _camera(marble, fps, lead=0.50, cam_dist=4.0):
    """Follow the marble right and down. Framing stays relative to the marble.

    The rig is not held inside a fixed world-height band. A relative clip only
    keeps the marble inside the 16:9 view while the whole view descends.
    """
    marble = np.asarray(marble, dtype=float)
    aim_z = -0.15
    cx = _smooth(marble[:, 0] + lead, fps, 0.50)
    cz = _smooth(marble[:, 1] - aim_z, fps, 0.28)
    vh = 2.0 * cam_dist * math.tan(math.atan(18.0 / 40.0))
    half = 0.38 * vh
    for _ in range(4):
        cz = np.clip(cz, marble[:, 1] - aim_z - half, marble[:, 1] - aim_z + half)
        cz = _smooth(cz, fps, 0.12)
    rig = dict(off=[0.0, -cam_dist, 0.8], aim=[0.0, 0.0, aim_z], lens=40,
               sensor_fit="VERTICAL", sensor=36, lead=lead,
               framing="relative to the marble; world z is not band-limited")
    return np.column_stack([cx, cz]), rig


def _frames(route):
    fps = route["fps"]
    g = route["g"]
    count = int(round(route["duration"] * fps)) + 1
    flights = route["flights"]
    frames = []
    for k in range(count):
        t = k / fps
        chosen = flights[0]
        for flight in flights:
            if flight["t0"] <= t + 1e-12:
                chosen = flight
            else:
                break
        p, _v = flight_state(chosen["p0"], chosen["v"], t - chosen["t0"], g)
        frames.append([float(p[0]), float(p[1])])
    return frames


def scene_plan(route, source_name=""):
    """Scene-style plan plus the descent audit block. Layout stays ``hscroll``."""
    frames = route.get("frame_override") or _frames(route)
    camera, rig = _camera(frames, route["fps"])
    frame_arr = np.asarray(frames, dtype=float)
    keys = []
    for c in route["contacts"]:
        normal = np.asarray(c["normal"], dtype=float)
        # The rendered marble and check_keepout both follow the sagged frames.
        # The plate is seated on that curve at the MIDI onset, not on the
        # analytic corner the chord cuts off between frames.
        centre = sag_at(frame_arr, c["time"], route["fps"], route["g"])
        origin = centre - normal * CONTACT_OFFSET
        keys.append(dict(
            i=c["i"], x=float(origin[0]), z=float(origin[1]),
            nx=float(normal[0]), nz=float(normal[1]), ang=math.atan2(float(normal[0]), float(normal[1])),
            tilt=math.degrees(math.acos(max(-1.0, min(1.0, abs(float(normal[1])))))),
            cx=float(centre[0]), cz=float(centre[1]), t=c["time"], t_audio=c["time"],
            note=route["hits"][c["i"]].get("note"), track=route["hits"][c["i"]]["track"],
            drum=route["hits"][c["i"]]["drum"], program=route["hits"][c["i"]].get("program"),
            side=1, family=f"L{c['layer']}", num=c["layer"] + 1,
            mount=c["mount"], pattern=c["pattern"], pattern_adapted=c["pattern_adapted"],
            layer=c["layer"], restitution=c["restitution"], kind=c["kind"],
        ))
    families = []
    instruments = []
    for key in keys:
        track = key["track"]
        if not instruments or instruments[-1]["track"] != track:
            instruments.append(dict(track=track, num=key["num"], family=key["family"],
                                    i0=key["i"], t0=key["t"], x0=key["x"]))
        instruments[-1].update(i1=key["i"], t1=key["t"], x1=key["x"])
        if not families or families[-1]["family"] != key["family"]:
            families.append(dict(family=key["family"], i0=key["i"], t0=key["t"], x0=key["x"]))
        families[-1].update(i1=key["i"], t1=key["t"], x1=key["x"])
    ballistics = [[f["t0"], f["p0"][0], f["p0"][1], f["v"][0], f["v"][1], f["t1"] - f["t0"]] for f in route["flights"]]
    summary = route["audit"]["summary"]
    return dict(
        fps=route["fps"], duration=route["duration"], R=MARBLE_RADIUS,
        KW=2.0 * route["plate_half"], KD=0.36, KH=2.0 * PLATE_RADIUS,
        g=route["g"], layout="hscroll", aspect="16:9",
        keys=keys, marble=frames, camera=camera.tolist(), cam_rig=rig,
        families=families, instruments=instruments, ballistics=ballistics,
        hscroll=dict(style="descent", seed=route["seed"], long_note=route["long_note"],
                     patterns=route["patterns"], lead=rig["lead"],
                     note="Optional template. v1, v2, portrait, and landscape/ are unchanged."),
        physics=dict(
            model="passive_frictionless", gravity=route["g"], restitution_max=1.0,
            energy_injection_allowed=False, tilt_max_deg=route["tilt_deg"],
            entry=route["entry"], plate_half_m=route["plate_half"], plate_radius_m=PLATE_RADIUS,
            marble_radius_m=MARBLE_RADIUS,
            bounds="Seeded score noise reorders candidates inside these bounds. It does not add velocity.",
        ),
        validation=dict(
            scope=route["scope"],
            whole_song=False,
            timing="exact MIDI hit times; frames are the same ballistic curve sampled at fps",
            clearance=summary["clearance_check"],
            clearance_margin_m=CLEARANCE_MARGIN,
            min_proxy_clearance_m=summary["min_proxy_clearance_m"],
            min_plate_proxy_clearance_m=summary["min_plate_proxy_clearance_m"],
            max_contact_penetration_m=summary["max_contact_penetration_m"],
            max_energy_gain_j_per_kg=summary["max_energy_gain_j_per_kg"],
            full_triangle_mesh=summary["full_triangle_mesh"],
            probe_point_keepout_pairs=summary["probe_point_keepout_pairs"],
            video_render="not run",
            source=source_name,
            landscape_template="separate; its 10-second anchors are not evidence for this route",
        ),
        descent=dict(
            route=_public_route(route),
            hits=route["hits"],
            backtracks=route["backtracks"],
            per_flight_proxy_clearance_m=summary["per_flight_proxy_clearance_m"],
        ),
        marble_spin=route.get("marble_spin_angle"),
    )


def _public_route(route):
    keep = ("status", "g", "seed", "fps", "duration", "scope", "long_note", "tilt_deg", "max_drop",
            "plate_half", "plate_radius", "marble_radius", "patterns", "layers", "contacts",
            "flights", "plates", "entry", "backtracks")
    return {key: route[key] for key in keep}


def plan_document(document, **kwargs):
    hits = document["hits"]
    duration = None
    if "end" in document and "start" in document:
        duration = float(document["end"]) - float(document["start"])
    scope = kwargs.pop("scope", None) or f"excerpt {document.get('start', 0)}–{document.get('end', hits[-1]['time'])} s"
    return plan_hits(hits, duration=duration, scope=scope, **kwargs)


def run_from_namespace(a):
    document = json.load(open(a.hits))
    g = 9.81 if getattr(a, "g", None) is None else a.g
    route = plan_document(
        document, g=g, seed=a.seed, fps=a.fps, tilt_deg=a.tilt_max, long_note=a.long_note,
        max_drop=a.descent_max_drop, plate_half=a.plate_half, patterns=a.patterns or "",
    )
    report_path = getattr(a, "report", "") or ""
    if route["status"] != "ok":
        payload = json.dumps(route, indent=2)
        if report_path:
            with open(report_path, "w", encoding="utf-8") as handle:
                handle.write(payload + "\n")
        else:
            stem = a.o.rsplit(".", 1)[0]
            with open(stem + ".impossible.json", "w", encoding="utf-8") as handle:
                handle.write(payload + "\n")
        print(route["message"])
        if route.get("violations"):
            for row in route["violations"][:12]:
                print(row)
        print("blocker:", route.get("blocker"), "hit", route.get("hit"), "t", route.get("time"),
              "layer", route.get("layer"), "pattern", route.get("pattern"), "mount", route.get("mount"),
              "backtracks", route.get("backtracks"))
        print("position", route.get("position"), "vin", route.get("incoming_velocity"), "rejects", route.get("reject_counts"))
        print("clearance failures", route.get("clear_fail"))
        if route.get("energy_deficit_j_per_kg") is not None:
            print(f"energy deficit vs preferred landing: {route['energy_deficit_j_per_kg']:.3f} J/kg")
        if route.get("shallowest_passive_drop_m") is not None:
            print(f"shallowest passive rightward drop: {route['shallowest_passive_drop_m']:.3f} m")
        for line in route.get("tradeoffs", [])[:4]:
            print("-", line)
        sys.exit(2)
    plan = scene_plan(route, source_name=document.get("midi", a.hits))
    with open(a.o, "w", encoding="utf-8") as handle:
        json.dump(plan, handle)
        handle.write("\n")
    if report_path:
        with open(report_path, "w", encoding="utf-8") as handle:
            json.dump(dict(ok=True, validation=plan["validation"], summary=route["audit"]["summary"]), handle, indent=2)
            handle.write("\n")
    z = [key["cz"] for key in plan["keys"]]
    print(f"descent: {len(plan['keys'])} hits, {route['patterns']} , z {max(z):.2f}..{min(z):.2f} m, "
          f"proxy clearance {plan['validation']['min_proxy_clearance_m']:.3f} m, "
          f"plate gap {plan['validation']['min_plate_proxy_clearance_m']:.3f} m, "
          f"max energy gain {plan['validation']['max_energy_gain_j_per_kg']:.3e} J/kg, "
          f"backtracks {route['backtracks']}")
    print("proxy check only; full triangle mesh and probe-point keep-out/pairs were not run; excerpt, not the whole song")
    return plan


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("hits")
    ap.add_argument("-o", required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--g", type=float, default=9.81)
    ap.add_argument("--seed", type=int, default=4)
    ap.add_argument("--tilt-max", type=float, default=60.0)
    add_args(ap)
    run_from_namespace(ap.parse_args(argv))


if __name__ == "__main__":
    main()
