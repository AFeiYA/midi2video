"""Stitch one passive guide into a descending-layer excerpt.

Hits before the chosen long note stay on the free passive plan. That note's
outgoing velocity is the guide's incoming velocity. The guide spends the
whole musical gap and lands on the next onset. Later hits are planned again
from that landing, still passive, still on the MIDI times.
"""

import json

import numpy as np
from scipy.spatial import cKDTree

from hscroll_descent.physics import outgoing_grid
from hscroll_descent.plan import CONTACT_OFFSET, plan_document, plan_hits, scene_plan
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
from hscroll_descent.rail import materialize_guide, plan_guided_hop
from hscroll_descent.rail_geometry import build_channel


def _guide_obstacles(guide):
    """Capsules along the groove, omitting the lip the marble is leaving."""
    plates = []
    for phase in guide["phases"]:
        if phase["name"] != "rail":
            continue
        samples = phase["samples"]
        body = samples[int(len(samples) * 0.15): max(2, int(len(samples) * 0.7))]
        for sample in body[::4]:
            plates.append(dict(
                center=np.array(sample["p"], float),
                normal=np.array([0.0, 1.0]),
                half_length=0.05,
                radius=0.06,
                contact=-1,
            ))
    return plates


def _guide_rows(guide, t0):
    rows = []
    cursor = float(t0)
    for phase in guide["phases"]:
        omega = 0.0
        for sample in phase["samples"]:
            if "omega" in sample:
                omega = float(sample["omega"])
            elif phase["name"] == "rail":
                omega = float(sample["speed"]) / guide["marble_radius_m"]
            vel = sample.get("v")
            rows.append(dict(
                t=cursor + float(sample["t"]),
                p=[float(sample["p"][0]), float(sample["p"][1])],
                v=[float(vel[0]), float(vel[1])] if vel is not None else [0.0, 0.0],
                omega=omega,
                phase=phase["name"],
            ))
        cursor += float(phase["duration_s"])
    return rows


def _ballistic(flight, t, g):
    u = t - flight["t0"]
    x = flight["p0"][0] + flight["v"][0] * u
    z = flight["p0"][1] + flight["v"][1] * u - 0.5 * g * u * u
    vx = flight["v"][0]
    vz = flight["v"][1] - g * u
    return [x, z], [vx, vz]


def _sample_guide(rows, t):
    if t <= rows[0]["t"]:
        return rows[0]
    if t >= rows[-1]["t"]:
        return rows[-1]
    for a, b in zip(rows, rows[1:]):
        if a["t"] <= t <= b["t"]:
            span = max(b["t"] - a["t"], 1e-9)
            w = (t - a["t"]) / span
            p = [(1 - w) * a["p"][k] + w * b["p"][k] for k in (0, 1)]
            v = [(1 - w) * a["v"][k] + w * b["v"][k] for k in (0, 1)]
            omega = (1 - w) * a["omega"] + w * b["omega"]
            return dict(t=t, p=p, v=v, omega=omega, phase=a["phase"])
    return rows[-1]


def _guide_release_ok(guide, channel, t0, fps, radius=0.15, gap=0.012):
    """Rendered frames after the lip clear the channel. Sub-steps do not penetrate."""
    cursor = float(t0)
    t_release = None
    for phase in guide["phases"]:
        cursor += float(phase["duration_s"])
        if phase["name"] == "rail":
            t_release = cursor
            break
    if t_release is None:
        return False
    # On a frame, or at most 0.4 ms late. Early would paint the 1 mm liftoff.
    frame = round(t_release * fps) / fps
    if not (frame - 1e-4 <= t_release <= frame + 6e-4):
        return False
    clouds = [np.asarray(channel["probes"][key], float) for key in ("floor", "wall", "bracket") if channel["probes"].get(key)]
    if not clouds:
        return False
    tree = cKDTree(np.vstack(clouds))
    exit_phase = guide["phases"][-1]
    p0 = np.asarray(exit_phase["p0"], float)
    v0 = np.asarray(exit_phase["v0"], float)
    g = float(guide["g"])
    t_land = float(t0) + float(guide["dt_s"])
    k = int(np.floor(t_release * fps + 1e-9)) + 1
    while k / fps < t_land - 1e-9:
        tau = k / fps - t_release
        point = p0 + v0 * tau + 0.5 * np.array([0.0, -g]) * tau * tau
        dist = float(tree.query([point[0], 0.0, point[1]], k=1)[0])
        if dist < radius + gap:
            return False
        k += 1
    step = 1.0 / (fps * 8.0)
    tau = step
    while tau < min(1.0 / fps, exit_phase["duration_s"]):
        point = p0 + v0 * tau + 0.5 * np.array([0.0, -g]) * tau * tau
        dist = float(tree.query([point[0], 0.0, point[1]], k=1)[0])
        if dist < radius - 5e-4:
            return False
        tau += step
    return True


def _frames_with_guide(base, guide, launch_index, flights):
    fps = base["fps"]
    g = base["g"]
    t0 = base["contacts"][launch_index]["time"]
    rows = _guide_rows(guide, t0)
    t1 = rows[-1]["t"]
    last = int(np.floor(t1 * fps + 1e-9))
    frames = []
    for k in range(last + 1):
        t = k / fps
        if rows[0]["t"] - 1e-9 <= t <= t1 + 1e-9:
            frames.append(_sample_guide(rows, t)["p"])
        else:
            chosen = flights[0]
            for flight in flights:
                if flight["t0"] <= t + 1e-12:
                    chosen = flight
            point, _vel = _ballistic(chosen, t, g)
            frames.append(point)
    return np.asarray(frames, float), rows


def _guide_respects_probes(base, guide, channel, launch_index, normal, library, prefix_placed):
    """Guide centre and the channel mesh stay off the strikers already placed.

    The launch striker is reseated on the sagged frame at its onset, because
    the outgoing frame is now the guide rather than the free hop.
    """
    flights = [f for f in base["flights"] if f.get("start_contact") is None or f["start_contact"] < launch_index]
    frames, rows = _frames_with_guide(base, guide, launch_index, flights)
    fps = base["fps"]
    g = base["g"]
    launch = base["contacts"][launch_index]
    centre = sag_at(frames, launch["time"], fps, g)
    origin = centre - np.asarray(normal, float) * CONTACT_OFFSET
    name = prefix_placed["names"][launch_index]
    variant = prefix_placed["variants"][launch_index]
    for earlier in prefix_placed["items"]:
        if pair_distance(library, name, variant, origin, normal, earlier) < PAIR_MIN:
            return False
    launch_item = Placement(library, name, variant, origin, normal, launch["time"])
    samples, times = sag_samples(frames, fps, g, sub=8)
    for item in list(prefix_placed["items"]) + [launch_item]:
        ok, _dist = keepout_against(item, samples, times, fps, SEARCH_KEEP)
        if not ok:
            return False
    clouds = [np.asarray(channel["probes"][key], float) for key in ("floor", "wall", "bracket") if channel["probes"].get(key)]
    if not clouds:
        return False
    rail_cloud = np.vstack(clouds)
    for item in list(prefix_placed["items"]) + [launch_item]:
        gap = obstacle_distance(rail_cloud, item.origin, item.normal, library, item.name, item.variant)
        if gap is not None and gap < PAIR_MIN:
            return False
    return True


def _prefix_assets(base, launch_index):
    """Placements for strikers before the launch. The launch itself is reseated per guide."""
    library = ProbeLibrary("v5")
    assigned = library.assign(base["hits"])
    frames = np.asarray(_frames_of(base), float)
    items = []
    for contact in base["contacts"][:launch_index]:
        name, variant, _j = assigned[contact["i"]]
        centre = sag_at(frames, contact["time"], base["fps"], base["g"])
        origin = centre - np.asarray(contact["normal"], float) * CONTACT_OFFSET
        items.append(Placement(library, name, variant, origin, contact["normal"], contact["time"]))
    return dict(
        library=library,
        items=items,
        names=[row[0] for row in assigned],
        variants=[row[1] for row in assigned],
    )


def _frames_of(route):
    from hscroll_descent.plan import _frames
    return _frames(route)


def _vout_choices(base, launch_index):
    launch = base["contacts"][launch_index]
    planned = (np.array(launch["vout"], float), np.array(launch["normal"], float), float(launch["restitution"]))
    grid = outgoing_grid(
        np.array(launch["vin"], float), launch["mount"], base["tilt_deg"], np.linspace(0.08, 1.0, 24),
    )
    ranked = []
    for vout, normal, restitution, _approach in grid:
        if np.linalg.norm(vout - planned[0]) < 1e-6:
            continue
        depart = float(np.asarray(vout) @ np.asarray(normal))
        ranked.append((-(restitution + 0.15 * depart), vout, normal, float(restitution)))
    ranked.sort(key=lambda row: row[0])
    choices = [(*planned, True)]
    for _score, vout, normal, restitution in ranked[:16]:
        choices.append((vout, normal, restitution, False))
    return choices


def build_guided_excerpt(document, seed=2, patterns="fold,fold,compact,shuttle", launch_index=9,
                         g=9.81, fps=30, tilt_deg=60.0, long_note=0.60):
    base = plan_document(
        document, g=g, seed=seed, fps=fps, tilt_deg=tilt_deg, long_note=long_note, patterns=patterns,
    )
    if base["status"] != "ok":
        return base
    contacts = base["contacts"]
    if launch_index >= len(contacts) - 1:
        return dict(status="refused", message="launch index is past the last hop")
    launch = contacts[launch_index]
    landing_hit = contacts[launch_index + 1]
    dt = landing_hit["time"] - launch["time"]
    previous_floor = min(c["p"][1] for c in contacts if c["layer"] == launch["layer"])
    prefix = _prefix_assets(base, launch_index)
    library = prefix["library"]
    chosen = None
    for vout, normal, restitution, _planned in _vout_choices(base, launch_index):
        accepted = []

        def accept(packed, vout=vout, normal=normal):
            if len(accepted) >= 4:
                return False
            (_score, t_fall, slide, rolled, p_cap, v_cap, _p_rail, v_exit, _p_land, _v_land,
             t_left, radius, _heading, center) = packed
            guide = materialize_guide(
                np.asarray(launch["p"], float), np.asarray(vout, float), g, dt, 0.0, 0.85,
                t_fall, slide, rolled, p_cap, v_cap, v_exit, t_left, radius, center,
            )
            if guide["landing"]["p"][1] >= previous_floor - 0.02:
                return False
            channel = build_channel(guide)
            if not _guide_release_ok(guide, channel, launch["time"], fps):
                return False
            if not _guide_respects_probes(base, guide, channel, launch_index, normal, library, prefix):
                return False
            accepted.append((guide, channel, np.asarray(normal, float), float(restitution), np.asarray(vout, float)))
            return True

        guide = plan_guided_hop(
            np.asarray(vout, float), dt, g=g, p0=launch["p"], t0=launch["time"], fps=fps, accept=accept,
        )
        if guide.get("status") != "ok" or not accepted:
            continue
        # The hopper returns the best score. Prefer a candidate the probe gate kept.
        for guide, channel, use_normal, use_e, use_vout in accepted:
            suffix = _suffix_after(document, base, guide, channel, launch_index, previous_floor, g, seed, fps, tilt_deg, long_note)
            if suffix is None or suffix.get("status") != "ok":
                continue
            launch_contact = dict(launch)
            launch_contact["vout"] = [float(use_vout[0]), float(use_vout[1])]
            launch_contact["normal"] = [float(use_normal[0]), float(use_normal[1])]
            launch_contact["restitution"] = use_e
            launch_contact["plate_center"] = (
                np.asarray(launch["p"], float) - use_normal * CONTACT_OFFSET
            ).tolist()
            merged = _merge(base, suffix, guide, launch_index, float(document["end"]) - float(document["start"]), document, launch_contact)
            from hscroll_descent.probes import audit_plan, rail_release_samples
            report = audit_plan(merged["plan"])
            release = rail_release_samples(merged["plan"])
            merged["plan"]["validation"]["strict_probe_keepout"] = report["keepout_ok"]
            merged["plan"]["validation"]["strict_probe_pairs"] = report["pairs_ok"]
            merged["plan"]["validation"]["rail_release_margin"] = release
            if report["keepout_ok"] and report["pairs_ok"] and release["ok"]:
                chosen = merged
                break
        if chosen is not None:
            break
    if chosen is None:
        return dict(
            status="refused", where="guide_or_suffix", powered_kicker=False, energy_was_relaxed=False,
            message="No passive guide and suffix clears full-resolution probes and the lip margin. Exit speed was not increased.",
        )
    return chosen


def _suffix_after(document, base, guide, channel, launch_index, previous_floor, g, seed, fps, tilt_deg, long_note):
    launch = base["contacts"][launch_index]
    rows = _guide_rows(guide, launch["time"])
    landing_t = rows[-1]["t"]
    f0 = int(np.floor(landing_t * fps + 1e-9))
    pins = []
    if f0 / fps < landing_t - 1e-6:
        sample = _sample_guide(rows, f0 / fps)
        pins.append([f0 / fps, sample["p"][0], sample["p"][1]])
    extra = []
    step = 1.0 / (fps * 8.0)
    t = rows[0]["t"]
    while t < landing_t - 1e-9:
        sample = _sample_guide(rows, t)
        extra.append([t, sample["p"][0], sample["p"][1]])
        t += step
    clouds = [np.asarray(channel["probes"][key], float) for key in ("floor", "wall", "bracket") if channel["probes"].get(key)]
    suffix_hits = base["hits"][launch_index + 1:]
    duration = float(document["end"]) - float(document["start"])
    return plan_hits(
        suffix_hits, g=g, seed=seed + 11, fps=fps, tilt_deg=tilt_deg, long_note=long_note,
        patterns="compact,shuttle,fold", duration=duration, scope=base["scope"],
        resume=dict(
            p=guide["landing"]["p"], v=guide["landing"]["v"], z_ceiling=previous_floor,
            pinned_frames=pins, extra_path=extra, obstacle_clouds=[np.vstack(clouds)],
        ),
        extra_plates=[],
    )


def _merge(base, suffix, guide, launch_index, duration, document, launch_contact=None):
    prefix = [dict(contact) for contact in base["contacts"][:launch_index + 1]]
    if launch_contact is not None:
        prefix[-1] = launch_contact
    # Drop the free hop that used to leave the launch contact.
    flights = [f for f in base["flights"] if f.get("start_contact") is None or f["start_contact"] < launch_index]
    offset = launch_index + 1
    suffix_contacts = []
    for contact in suffix["contacts"]:
        copied = dict(contact)
        copied["i"] = contact["i"] + offset
        copied["layer"] = contact["layer"] + prefix[-1]["layer"] + 1
        suffix_contacts.append(copied)
    for flight in suffix["flights"]:
        if flight["role"] == "resume":
            continue
        copied = dict(flight)
        if copied.get("start_contact") is not None:
            copied["start_contact"] += offset
        if copied.get("end_contact") is not None:
            copied["end_contact"] += offset
        flights.append(copied)
    contacts = prefix + suffix_contacts
    hits = base["hits"][:offset] + [
        dict(hit, time=suffix["hits"][k]["time"]) for k, hit in enumerate(base["hits"][offset:])
    ]
    guide_rows = _guide_rows(guide, prefix[-1]["time"])
    g = base["g"]
    fps = base["fps"]
    count = int(round(duration * fps)) + 1
    frames = []
    omegas = []
    spin = 0.0
    prev_t = 0.0
    t_guide0, t_guide1 = guide_rows[0]["t"], guide_rows[-1]["t"]
    for frame in range(count):
        t = frame / fps
        if t_guide0 - 1e-9 <= t <= t_guide1 + 1e-9:
            sample = _sample_guide(guide_rows, t)
            point, omega = sample["p"], sample["omega"]
        else:
            chosen = flights[0]
            for flight in flights:
                if flight["t0"] <= t + 1e-12:
                    chosen = flight
            point, _vel = _ballistic(chosen, t, g)
            omega = omegas[-1] if omegas else 0.0
        if frames:
            spin += omega * (t - prev_t)
        frames.append([float(point[0]), float(point[1])])
        omegas.append(float(omega))
        prev_t = t
    route = dict(base)
    route.update(
        contacts=contacts, flights=flights, hits=hits, duration=duration,
        frame_override=frames, marble_omega=omegas, marble_spin_angle=_spin_angles(omegas, fps),
        guide=guide, guide_rows=[{k: row[k] for k in ("t", "p", "v", "omega", "phase")} for row in guide_rows],
    )
    # scene_plan audits route["audit"], which is the prefix audit. Replace it
    # with a stitched note so the scene export does not claim the old landing.
    route["audit"] = dict(base["audit"])
    route["audit"]["summary"] = dict(base["audit"]["summary"])
    route["audit"]["summary"]["guide"] = "one passive transition replaces one long hop; see guide_rail.validation"
    plan = scene_plan(route, source_name=document.get("midi", ""))
    plan["marble"] = frames
    plan["marble_spin"] = route["marble_spin_angle"]
    channel = build_channel(guide)
    plan["guide_rail"] = dict(
        renderer_supported=True,
        optional=True,
        launch_hit=launch_index,
        landing_hit=launch_index + 1,
        t0=guide_rows[0]["t"],
        t1=guide_rows[-1]["t"],
        material=channel["material"],
        support_material=channel["support_material"],
        principles=channel["principles"],
        not_a_manufactured_replica=True,
        verts=channel["verts"],
        faces=channel["faces"],
        probes=channel["probes"],
        stations=channel["stations"],
        marble_radius_m=channel["marble_radius_m"],
        half_width_m=channel["half_width_m"],
        energy_model=guide["assumption"],
        powered_kicker=False,
        phases=[
            dict(name=phase["name"], kind=phase["kind"], duration_s=phase["duration_s"],
                 force=phase.get("force"), work_j_per_kg=phase.get("work_j_per_kg"),
                 energy_loss_j_per_kg=phase.get("energy_loss_j_per_kg"),
                 z_entry=phase.get("z_entry"), z_valley=phase.get("z_valley"), z_exit=phase.get("z_exit"))
            for phase in guide["phases"]
        ],
    )
    plan["validation"]["timing"] = (
        "MIDI onsets preserved. Free hops are parabolas. The guide interval is the sampled centerline."
    )
    plan["validation"]["guide_geometry"] = "authored channel follows the guide centerline; full triangle mesh not run"
    plan["hscroll"]["guide"] = "one passive banked hairpin and jump-chute lip on a single long note"
    return dict(status="ok", plan=plan, guide=guide, base_launch=launch_index)


def _spin_angles(omegas, fps):
    angle = 0.0
    out = []
    for i, omega in enumerate(omegas):
        if i:
            angle += omega / fps
        out.append(float(angle))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("hits")
    ap.add_argument("-o", required=True)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--launch-index", type=int, default=9)
    ap.add_argument("--patterns", default="fold,fold,compact,shuttle")
    args = ap.parse_args()
    document = json.load(open(args.hits))
    result = build_guided_excerpt(document, seed=args.seed, patterns=args.patterns, launch_index=args.launch_index)
    if result.get("status") != "ok":
        print(result.get("status"), result.get("where"), result.get("message", "")[:400])
        raise SystemExit(2)
    with open(args.o, "w", encoding="utf-8") as handle:
        json.dump(result["plan"], handle)
        handle.write("\n")
    rail = result["plan"]["guide_rail"]
    print(f"guided excerpt: {len(result['plan']['keys'])} hits, rail hits {rail['launch_hit']}->{rail['landing_hit']}, "
          f"stations {len(rail['stations'])}, brackets in probe set {len(rail['probes']['bracket'])}")


if __name__ == "__main__":
    main()
