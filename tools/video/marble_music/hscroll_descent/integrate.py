"""Stitch one passive guide into a descending-layer excerpt.

Hits before the chosen long note stay on the free passive plan. That note's
outgoing velocity is the guide's incoming velocity. The guide spends the
whole musical gap and lands on the next onset. Later hits are planned again
from that landing, still passive, still on the MIDI times.
"""

import json

import numpy as np

from hscroll_descent.plan import plan_document, plan_hits, scene_plan
from hscroll_descent.rail import plan_guided_hop
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
    guide = plan_guided_hop(np.array(launch["vout"]), dt, g=g, p0=launch["p"])
    if guide["status"] != "ok":
        guide["where"] = "guide"
        return guide
    rail_phase = next(phase for phase in guide["phases"] if phase["name"] == "rail")
    rail_ceiling = rail_phase["z_valley"] - 0.35
    previous_floor = min(c["p"][1] for c in contacts if c["layer"] == launch["layer"])
    z_ceiling = min(previous_floor, rail_ceiling)
    suffix_hits = base["hits"][launch_index + 1:]
    duration = float(document["end"]) - float(document["start"])
    suffix = plan_hits(
        suffix_hits, g=g, seed=seed + 11, fps=fps, tilt_deg=tilt_deg, long_note=long_note,
        patterns="compact,shuttle,fold", duration=duration, scope=base["scope"],
        resume=dict(p=guide["landing"]["p"], v=guide["landing"]["v"], z_ceiling=previous_floor),
        extra_plates=[],
    )
    if suffix["status"] != "ok":
        suffix["where"] = "suffix_after_guide"
        return suffix
    merged = _merge(base, suffix, guide, launch_index, duration, document)
    return merged


def _merge(base, suffix, guide, launch_index, duration, document):
    prefix = base["contacts"][:launch_index + 1]
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
