"""Probe checks for a guided excerpt.

Strikers are judged by the same full-resolution v5 clouds as
``check_keepout.py --look v5`` and ``check_pairs.py --look v5``. The guide
uses the authored channel samples. Floor contact while the marble is on the
capture or the groove is the intended roll. After release, every rendered
frame must clear the channel by 12 mm. A full triangle mesh is still not run.
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INST = os.path.join(os.path.dirname(HERE), "assets", "instruments")


def _load_library():
    if INST not in sys.path:
        sys.path.insert(0, INST)
    import library
    return library


def _rail_clearance(plan):
    rail = plan["guide_rail"]
    radius = plan["R"]
    marble = np.asarray(plan["marble"], float)
    fps = plan["fps"]
    t0, t1 = rail["t0"], rail["t1"]
    # The channel exists only for capture + groove. Times come from phases.
    on = []
    off = []
    for i, (x, z) in enumerate(marble):
        t = i / fps
        # Capture starts after the free fall. Use station span: the first
        # station is the capture entrance and the last is the lip.
        if t0 <= t <= t1 and _phase_at(plan, t) in ("capture", "rail"):
            on.append((x, z))
        else:
            off.append((x, z))
    floor = np.asarray(rail["probes"]["floor"], float)
    walls = np.asarray(rail["probes"]["wall"], float) if rail["probes"]["wall"] else np.zeros((0, 3))
    brackets = np.asarray(rail["probes"]["bracket"], float) if rail["probes"]["bracket"] else np.zeros((0, 3))
    obstacles = np.vstack([a for a in (walls, brackets) if len(a)])

    def nearest(points, cloud):
        if not len(points) or not len(cloud):
            return None
        pts = np.asarray(points, float)
        xyz = np.c_[pts[:, 0], np.zeros(len(pts)), pts[:, 1]]
        # Chunk so a long excerpt does not build a giant matrix.
        best = np.full(len(pts), np.inf)
        step = 64
        for start in range(0, len(cloud), step):
            block = cloud[start:start + step]
            dist = np.linalg.norm(xyz[:, None, :] - block[None, :, :], axis=2)
            best = np.minimum(best, dist.min(axis=1))
        return best

    floor_on = nearest(on, floor)
    wall_on = nearest(on, obstacles)
    obstacle_off = nearest(off, np.vstack([floor, obstacles]) if len(obstacles) else floor)
    return dict(
        check="authored guide samples, not a CAD mesh boolean",
        floor_contact_m=dict(min=float(floor_on.min()), median=float(np.median(floor_on)), max=float(floor_on.max())),
        obstacle_while_riding_m=None if wall_on is None else float(wall_on.min()),
        obstacle_while_airborne_m=None if obstacle_off is None else float(obstacle_off.min()),
        floor_target_m=radius,
        riding_frames=len(on),
    )


def _phase_at(plan, t):
    guide = plan.get("descent", {}).get("route", {}).get("guide_rows")
    # guide rows are not on the public route. Use guide_rail phases only as a
    # time split: capture+rail are the middle of [t0, t1] after the fall.
    rail = plan["guide_rail"]
    for phase in rail["phases"]:
        pass
    # Fall is first and airborne. Capture and rail are the channel.
    cursor = rail["t0"]
    for phase in rail["phases"]:
        end = cursor + phase["duration_s"]
        if cursor - 1e-9 <= t <= end + 1e-9:
            return phase["name"]
        cursor = end
    return "exit_flight"


def _instrument_keepout(plan, look="v5"):
    from hscroll_descent.probes import audit_plan
    report = audit_plan(plan, look=look, sub=8)
    return dict(
        check="full-resolution v5 y-slab probes, gravity-sag path, outside each key's own 1.2-frame hit window",
        full_triangle_mesh="not run",
        violations=report["violations"],
        clashes=report["clashes"],
        pairs_ok=report["pairs_ok"],
        closest=[dict(dist_m=row[0], key=row[1], asset=row[2]) for row in report["closest"][:8]],
    )


def validate(plan, look="v5"):
    from hscroll_descent.probes import rail_release_samples
    rail = _rail_clearance(plan)
    instruments = _instrument_keepout(plan, look=look)
    release = rail_release_samples(plan, sub=8)
    radius = plan["R"]
    riding_ok = (
        abs(rail["floor_contact_m"]["median"] - radius) < 0.02
        and rail["floor_contact_m"]["min"] > radius - 0.01
        and (rail["obstacle_while_riding_m"] or 0) >= radius + 0.004
    )
    # Airborne samples include the continuous liftoff. The release report,
    # not a single nearest sample, decides whether that liftoff is a graze.
    ok = riding_ok and release["ok"] and not instruments["violations"] and instruments["pairs_ok"]
    return dict(
        ok=ok,
        strict_instrument_keepout_0_97R=not instruments["violations"],
        strict_pairs_1cm=instruments["pairs_ok"],
        rail=rail,
        release=release,
        instruments=instruments,
        proxy_plate_clearance=plan["validation"].get("clearance"),
        exemptions=dict(
            striker_hit="within 1.2 frames of that key's own onset",
            rail_roll="floor samples while the phase is capture or rail; walls and brackets are never exempt",
        ),
        labels=dict(
            guide="authored channel samples along the centerline",
            strikers="full-resolution v5 probe clouds, same rule as check_keepout.py and check_pairs.py",
            plates="capsule proxy from the descent audit",
            full_triangle_mesh="not run",
        ),
    )


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plan")
    ap.add_argument("-o", default="")
    ap.add_argument("--look", default="v5")
    args = ap.parse_args()
    plan = json.load(open(args.plan))
    report = validate(plan, look=args.look)
    text = json.dumps(report, indent=2)
    if args.o:
        with open(args.o, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text)
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
