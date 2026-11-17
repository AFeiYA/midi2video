"""Probe checks for a guided excerpt.

Instrument strikers use the checked-in v5 probe clouds, subsampled. That is
not a full triangle-mesh sweep. The guide uses the authored channel samples
(floor, walls, brackets). During the ride the floor is the target surface;
walls, brackets, and every other striker are obstacles.
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


def _instrument_keepout(plan, look="v5", stride=8):
    library = _load_library()
    metas = library.metas(look)
    assigned = library.assign(plan["keys"], metas, plan.get("instrument_set"))
    radius = plan["R"]
    fps = plan["fps"]
    marble = np.asarray(plan["marble"], float)
    times = np.arange(len(marble)) / fps
    probes = {}
    violations = []
    closest = []
    for key, (name, variant, _j) in zip(plan["keys"], assigned):
        meta = metas[name]
        cloud = probes.get((name, variant))
        if cloud is None:
            cloud = np.load(os.path.join(meta["_dir"], f"probe_{variant}.npy")).astype(np.float64)[::stride]
            probes[(name, variant)] = cloud
        slab = cloud[np.abs(cloud[:, 1]) < radius]
        if not len(slab):
            continue
        nx, nz = key["nx"], key["nz"]
        tx, tz = nz, -nx
        world = np.c_[
            key["x"] + slab[:, 0] * tx + slab[:, 2] * nx,
            slab[:, 1],
            key["z"] + slab[:, 0] * tz + slab[:, 2] * nz,
        ]
        near = (np.abs(marble[:, 0] - key["x"]) < 1.4) & (np.abs(marble[:, 1] - key["z"]) < 1.4)
        idx = np.flatnonzero(near & (np.abs(times - key["t"]) >= 1.2 / fps))
        if not len(idx):
            continue
        best = np.inf
        worst_i = None
        for start in range(0, len(idx), 40):
            block = idx[start:start + 40]
            xyz = np.c_[marble[block, 0], np.zeros(len(block)), marble[block, 1]]
            dist = np.linalg.norm(xyz[:, None, :] - world[None, :, :], axis=2).min(axis=1)
            j = int(np.argmin(dist))
            if dist[j] < best:
                best = float(dist[j])
                worst_i = int(block[j])
        closest.append(dict(key=key["i"], asset=name, dist_m=best))
        if best < 0.97 * radius:
            violations.append(dict(key=key["i"], asset=name, dist_m=best, frame=worst_i,
                                   check="subsampled v5 probe cloud, y slab, not a full triangle sweep"))
    closest.sort(key=lambda row: row["dist_m"])
    return dict(
        check="subsampled library probes (stride %d), y-slab |y|<R, outside each key's own hit window" % stride,
        full_triangle_mesh="not run",
        violations=violations,
        closest=closest[:8],
    )


def validate(plan, look="v5"):
    rail = _rail_clearance(plan)
    instruments = _instrument_keepout(plan, look=look)
    radius = plan["R"]
    guide_ok = (
        abs(rail["floor_contact_m"]["median"] - radius) < 0.02
        and rail["floor_contact_m"]["min"] > radius - 0.01
        and (rail["obstacle_while_riding_m"] or 0) >= radius + 0.005
        and (rail["obstacle_while_airborne_m"] or 0) >= radius - 0.002
    )
    return dict(
        ok=guide_ok,
        strict_instrument_keepout_0_97R=not instruments["violations"],
        rail=rail,
        instruments=instruments,
        proxy_plate_clearance=plan["validation"].get("clearance"),
        labels=dict(
            guide="authored channel samples along the centerline",
            strikers="subsampled v5 probe clouds; 0.97R keep-out is reported separately and is not claimed when it fails",
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
