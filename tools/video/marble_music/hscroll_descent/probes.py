"""Full-resolution striker probes for the descent search and the final gate.

``check_keepout.py --look v5`` uses every probe with ``|y| < R`` and the
gravity-sag path between frames. ``check_pairs.py --look v5`` uses every
other probe of the whole asset. The search consults those clouds. A capsule
around the contact plate is not a substitute.

Two exemptions, and no others:

- A key's own probes inside 1.2 frames of its own onset. That is the strike.
- Rail floor samples while the marble is still on the capture or the groove.
  Walls, brackets, and every sample after release stay obstacles.

The lip is a tangent release. Distance to the last contact grows from R.
A rendered frame after release must clear R by ``RELEASE_GAP``. Samples
between that frame and the contact may lift off, and they may not penetrate.
"""

import math
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

MARBLE_RADIUS = 0.15
CONTACT_OFFSET = 0.195          # R + plate radius 0.045, same as plan.py
STRICT_FACTOR = 0.97
SEARCH_KEEP = STRICT_FACTOR * MARBLE_RADIUS
PAIR_MIN = 0.012                # check_pairs flags 1.0 cm; the search stays above that
RELEASE_GAP = 0.012
HIT_WINDOW_FRAMES = 1.2

HERE = os.path.dirname(os.path.abspath(__file__))
INST = os.path.join(os.path.dirname(HERE), "assets", "instruments")


def _library():
    if INST not in sys.path:
        sys.path.insert(0, INST)
    import library
    return library


def sag_at(frames, t, fps, g):
    """Marble centre the keep-out script reconstructs at time ``t``."""
    frames = np.asarray(frames, float)
    fps = float(fps)
    f = float(t) * fps
    f0 = int(math.floor(f + 1e-9))
    f0 = max(0, min(f0, len(frames) - 1))
    f1 = min(f0 + 1, len(frames) - 1)
    u = 0.0 if f1 == f0 else f - math.floor(f + 1e-9)
    x = frames[f0, 0] * (1.0 - u) + frames[f1, 0] * u
    z = frames[f0, 1] * (1.0 - u) + frames[f1, 1] * u
    if f1 != f0:
        z += 0.5 * float(g) * (u / fps) * ((1.0 - u) / fps)
    return np.array([x, z], dtype=float)


def visual_plate(frames, t, normal, fps, g, offset=CONTACT_OFFSET):
    """Plate origin whose contact point is the sagged marble at the onset."""
    centre = sag_at(frames, t, fps, g)
    normal = np.asarray(normal, float)
    normal = normal / max(float(np.linalg.norm(normal)), 1e-12)
    origin = centre - normal * float(offset)
    return origin, centre


def world_points(local, origin_xz, normal):
    """Same placement as ``check_keepout.py`` and ``scene.py``."""
    local = np.asarray(local, float)
    nx, nz = float(normal[0]), float(normal[1])
    tx, tz = nz, -nx
    out = np.empty((len(local), 3), dtype=float)
    out[:, 0] = origin_xz[0] + local[:, 0] * tx + local[:, 2] * nx
    out[:, 1] = local[:, 1]
    out[:, 2] = origin_xz[1] + local[:, 0] * tz + local[:, 2] * nz
    return out


def _voxel(points, size):
    if not len(points):
        return points
    quant = np.round(np.asarray(points, float) / size).astype(np.int64)
    _unique, index = np.unique(quant, axis=0, return_index=True)
    return np.asarray(points, float)[np.sort(index)]


class ProbeLibrary:
    def __init__(self, look="v5"):
        library = _library()
        self.look = look
        self.metas = library.metas(look)
        self._assign = library.assign
        self._cache = {}

    def assign(self, hits):
        stubs = []
        for i, hit in enumerate(hits):
            stubs.append(dict(
                i=i,
                track=hit.get("track_name", hit.get("track", "")),
                note=int(hit.get("note") or 60),
                drum=bool(hit.get("drum", False)),
                program=hit.get("program"),
            ))
        return self._assign(stubs, self.metas)

    def _entry(self, name, variant):
        key = (name, variant)
        if key in self._cache:
            return self._cache[key]
        meta = self.metas[name]
        cloud = np.load(os.path.join(meta["_dir"], f"probe_{variant}.npy")).astype(np.float64)
        slab = cloud[np.abs(cloud[:, 1]) < MARBLE_RADIUS]
        pair = cloud[::2]
        entry = dict(
            yslab=slab,
            pair=pair,
            coarse=_voxel(pair, 0.02),
            y_min=slab.min(0) if len(slab) else np.zeros(3),
            y_max=slab.max(0) if len(slab) else np.zeros(3),
            p_min=pair.min(0) if len(pair) else np.zeros(3),
            p_max=pair.max(0) if len(pair) else np.zeros(3),
        )
        self._cache[key] = entry
        return entry

    def yslab(self, name, variant):
        return self._entry(name, variant)["yslab"]

    def pair(self, name, variant):
        return self._entry(name, variant)["pair"]

    def coarse(self, name, variant):
        return self._entry(name, variant)["coarse"]


def _corners(lo, hi):
    pts = []
    for x in (lo[0], hi[0]):
        for y in (lo[1], hi[1]):
            for z in (lo[2], hi[2]):
                pts.append((x, y, z))
    return np.asarray(pts, float)


def world_aabb(local_lo, local_hi, origin_xz, normal):
    corners = world_points(_corners(local_lo, local_hi), origin_xz, normal)
    return corners.min(0), corners.max(0)


def aabb_gap(a_lo, a_hi, b_lo, b_hi):
    gap = np.maximum(a_lo - b_hi, b_lo - a_hi)
    return float(np.max(gap)) if np.all(np.isfinite(gap)) else 0.0


class Placement:
    def __init__(self, library, name, variant, origin_xz, normal, hit_time):
        entry = library._entry(name, variant)
        self.name = name
        self.variant = variant
        self.origin = np.asarray(origin_xz, float)
        self.normal = np.asarray(normal, float)
        self.time = float(hit_time)
        self.yslab = world_points(entry["yslab"], self.origin, self.normal)
        self.pair = world_points(entry["pair"], self.origin, self.normal)
        self.coarse = world_points(entry["coarse"], self.origin, self.normal)
        self.y_tree = cKDTree(self.yslab) if len(self.yslab) else None
        self.coarse_tree = cKDTree(self.coarse) if len(self.coarse) else None
        self.aabb = world_aabb(entry["y_min"], entry["y_max"], self.origin, self.normal)
        self.pair_aabb = world_aabb(entry["p_min"], entry["p_max"], self.origin, self.normal)


def _near_mask(samples, origin_xz, reach):
    return (np.abs(samples[:, 0] - origin_xz[0]) < reach) & (np.abs(samples[:, 2] - origin_xz[1]) < reach)


def min_outside_window(tree, samples, times, hit_time, fps, reach_origin, reach):
    """Nearest probe distance for samples outside the strike window."""
    if tree is None or not len(samples):
        return None
    window = HIT_WINDOW_FRAMES / float(fps)
    outside = np.abs(times - hit_time) >= window - 1e-12
    if reach_origin is not None:
        outside &= _near_mask(samples, reach_origin, reach)
    use = samples[outside]
    if not len(use):
        return None
    dist, _idx = tree.query(use, k=1, distance_upper_bound=reach)
    finite = dist[np.isfinite(dist)]
    if not len(finite):
        return None
    return float(finite.min())


def pair_distance(library, name, variant, origin, normal, other):
    """Minimum distance using the check_pairs stride, with a coarse reject."""
    if aabb_gap(other.pair_aabb[0], other.pair_aabb[1], *_aabb_of(library, name, variant, origin, normal)) > PAIR_MIN:
        return PAIR_MIN + 1.0
    entry = library._entry(name, variant)
    coarse = world_points(entry["coarse"], origin, normal)
    if other.coarse_tree is None or not len(coarse):
        return PAIR_MIN + 1.0
    dist, _idx = other.coarse_tree.query(coarse, k=1, distance_upper_bound=0.08)
    finite = dist[np.isfinite(dist)]
    if not len(finite):
        return 0.08
    coarse_min = float(finite.min())
    # 2 cm voxels can hide a closer full-stride pair by about one voxel diagonal.
    if coarse_min >= PAIR_MIN + 0.036:
        return coarse_min
    if coarse_min < PAIR_MIN:
        return coarse_min
    full = world_points(entry["pair"], origin, normal)
    tree = cKDTree(full)
    dist, _idx = tree.query(other.pair, k=1, distance_upper_bound=0.05)
    finite = dist[np.isfinite(dist)]
    if not len(finite):
        return 0.05
    return float(finite.min())


def _aabb_of(library, name, variant, origin, normal):
    entry = library._entry(name, variant)
    return world_aabb(entry["p_min"], entry["p_max"], origin, normal)


def obstacle_distance(points, origin, normal, library, name, variant):
    """Distance from a fixed cloud (the rail) to one striker. No exemption."""
    if points is None or not len(points):
        return None
    entry = library._entry(name, variant)
    coarse = world_points(entry["coarse"], origin, normal)
    tree = cKDTree(points)
    dist, _idx = tree.query(coarse, k=1, distance_upper_bound=0.08)
    finite = dist[np.isfinite(dist)]
    if not len(finite):
        return 0.08
    coarse_min = float(finite.min())
    if coarse_min >= PAIR_MIN + 0.036 or coarse_min < PAIR_MIN:
        return coarse_min
    full = world_points(entry["pair"], origin, normal)
    dist, _idx = tree.query(full, k=1, distance_upper_bound=0.05)
    finite = dist[np.isfinite(dist)]
    if not len(finite):
        return 0.05
    return float(finite.min())


def sag_samples(frames, fps, g, sub=8, t_min=None, t_max=None):
    """Path samples matching ``check_keepout.py`` (chord plus gravity sag)."""
    frames = np.asarray(frames, float)
    fps = float(fps)
    if len(frames) < 2:
        return np.zeros((0, 3)), np.zeros(0)
    step = 1.0 / (fps * sub)
    t1 = (len(frames) - 1) / fps
    ts = np.arange(0.0, t1, step)
    if t_min is not None:
        ts = ts[ts >= t_min - 1e-12]
    if t_max is not None:
        ts = ts[ts <= t_max + 1e-12]
    if not len(ts):
        return np.zeros((0, 3)), np.zeros(0)
    f0 = np.floor(ts * fps + 1e-12).astype(int)
    u = ts * fps - f0
    f1 = np.minimum(f0 + 1, len(frames) - 1)
    x = frames[f0, 0] * (1.0 - u) + frames[f1, 0] * u
    z = frames[f0, 1] * (1.0 - u) + frames[f1, 1] * u + 0.5 * float(g) * (u / fps) * ((1.0 - u) / fps)
    samples = np.c_[x, np.zeros(len(ts)), z]
    return samples, ts


def keepout_against(placement, samples, times, fps, limit):
    if placement.y_tree is None:
        return True, None
    dist = min_outside_window(placement.y_tree, samples, times, placement.time, fps, placement.origin, 1.6)
    if dist is None:
        return True, None
    return dist >= limit, dist


def release_clear(samples, radius=MARBLE_RADIUS, gap=RELEASE_GAP):
    """``samples`` are ``(tau_seconds, distance_m, rendered_frame)`` after contact.

    A rendered frame must sit at least ``gap`` outside the marble. Samples
    before the next frame are the continuous liftoff and may start at ``radius``.
    """
    for tau, dist, rendered in samples:
        if tau <= 1e-9:
            continue
        if dist < radius - 5e-4:
            return False
        if rendered and dist < radius + gap - 1e-9:
            return False
    return True


def _phase_end_times(rail):
    cursor = float(rail["t0"])
    ends = {}
    for phase in rail["phases"]:
        cursor += float(phase["duration_s"])
        ends[phase["name"]] = cursor
    return ends


def _cloud_distance(tree, points):
    if tree is None or not len(points):
        return None
    dist, _idx = tree.query(np.asarray(points, float), k=1)
    return dist


def rail_release_samples(plan, sub=8):
    """Distance from the marble to every rail sample after the groove lets go.

    Capture and groove floor contact is not in this list. Rendered frames are
    the plan's own frames (what the parent draws). Sub-steps only have to
    avoid penetration, because a tangent release leaves from distance R.
    """
    rail = plan["guide_rail"]
    ends = _phase_end_times(rail)
    t_release = ends.get("rail")
    if t_release is None:
        return dict(ok=False, reason="no rail phase")
    frames = np.asarray(plan["marble"], float)
    fps = float(plan["fps"])
    g = float(plan["g"])
    radius = float(plan["R"])
    clouds = []
    for key in ("floor", "wall", "bracket"):
        block = np.asarray(rail["probes"].get(key) or [], float)
        if len(block):
            clouds.append(block)
    cloud = np.vstack(clouds) if clouds else np.zeros((0, 3))
    tree = cKDTree(cloud) if len(cloud) else None
    rows = []
    worst_frame = None
    worst_any = None
    penetrated = False
    for index, (x, z) in enumerate(frames):
        t = index / fps
        tau = t - t_release
        if tau <= 1e-6:
            continue
        point = np.array([x, 0.0, z])
        dist = float(tree.query(point, k=1)[0]) if tree is not None else 1e9
        rows.append((tau, dist, True))
        if worst_frame is None or dist < worst_frame[0]:
            worst_frame = (dist, tau)
    samples, ts = sag_samples(frames, fps, g, sub=sub, t_min=t_release)
    if tree is not None and len(samples):
        dist = _cloud_distance(tree, samples)
        for d, t in zip(dist, ts):
            tau = float(t - t_release)
            if tau <= 1e-6:
                continue
            if d < radius - 5e-4:
                penetrated = True
            if worst_any is None or d < worst_any[0]:
                worst_any = (float(d), tau)
            rows.append((tau, float(d), False))
    on_frame = abs(t_release * fps - round(t_release * fps)) <= 0.06
    return dict(
        ok=release_clear(rows, radius=radius) and not penetrated and on_frame,
        t_release=float(t_release),
        release_on_frame=bool(on_frame),
        penetrated=penetrated,
        closest_after=(None if worst_any is None else dict(dist_m=worst_any[0], tau_s=worst_any[1])),
        closest_rendered_frame=(None if worst_frame is None else dict(dist_m=worst_frame[0], tau_s=worst_frame[1])),
        rendered_frames=sum(1 for row in rows if row[2]),
    )


def audit_plan(plan, look="v5", sub=8):
    """Same clouds and thresholds as the strict scripts. Returns their verdicts."""
    library = ProbeLibrary(look)
    keys = plan["keys"]
    assigned = library.assign(keys)
    frames = np.asarray(plan["marble"], float)
    fps = float(plan["fps"])
    g = float(plan["g"])
    radius = float(plan["R"])
    samples, ts = sag_samples(frames, fps, g, sub=sub)
    limit = STRICT_FACTOR * radius
    violations = []
    closest = []
    placed = []
    for key, (name, variant, _j) in zip(keys, assigned):
        origin = np.array([key["x"], key["z"]], float)
        normal = np.array([key["nx"], key["nz"]], float)
        item = Placement(library, name, variant, origin, normal, key["t"])
        placed.append(item)
        ok, dist = keepout_against(item, samples, ts, fps, limit)
        if dist is not None:
            closest.append((dist, key["i"], name))
        if not ok:
            violations.append(dict(key=key["i"], asset=name, dist_m=dist))
    clashes = []
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            if aabb_gap(placed[i].pair_aabb[0], placed[i].pair_aabb[1],
                        placed[j].pair_aabb[0], placed[j].pair_aabb[1]) > 0.01:
                continue
            dist, _idx = cKDTree(placed[j].pair).query(placed[i].pair, k=1, distance_upper_bound=0.2)
            finite = dist[np.isfinite(dist)]
            gap = float(finite.min()) if len(finite) else 0.2
            if gap < 0.01:
                clashes.append(dict(dist_m=gap, keys=[keys[i]["i"], keys[j]["i"]],
                                     assets=[placed[i].name, placed[j].name]))
    closest.sort()
    return dict(
        keepout_ok=not violations,
        pairs_ok=not clashes,
        violations=violations,
        clashes=clashes,
        closest=closest[:8],
        limit_m=limit,
    )
