"""Channel, bank, and brackets from a guide centerline. No Blender.

The marble center is the validated path. The floor sits one marble radius
off that center, the side walls stand outside the ball, and the brackets run
back to the wall from those same stations. Nothing is drawn off the path.

Banking follows the hairpin in US5007876A: through the turn the wall toward
the back of the stage rises, so the lane is not a flat ribbon. The exit
follows the jump chute in US4874342A: the walls taper off an upturned lip and
the marble leaves on the tangent. These are borrowed principles, not copies.
"""

import numpy as np

MARBLE_RADIUS = 0.15
HALF_WIDTH = 0.195
FLOOR_THICK = 0.014
WALL_INNER = 0.09
WALL_OUTER = 0.17
BRACKET_EVERY = 0.42
WALL_Y_TARGET = 0.30  # hscroll wall, KD/2 + 0.12 with KD = 0.36


def _unit(v):
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    if n < 1e-9:
        return np.zeros(3)
    return v / n


def _up_normal(tangent_xz):
    tx, tz = float(tangent_xz[0]), float(tangent_xz[1])
    cand = np.array([-tz, 0.0, tx])
    if cand[2] < 0:
        cand = -cand
    return _unit(cand)


def centerline_from_guide(guide):
    """Slip capture plus the rolling groove. Free fall and the jump stay airborne."""
    rows = []
    for phase in guide["phases"]:
        if phase["name"] not in ("capture", "rail"):
            continue
        for sample in phase["samples"]:
            tangent = sample.get("tangent")
            if tangent is None:
                vel = np.asarray(sample["v"], float)
                tangent = (vel / max(np.linalg.norm(vel), 1e-9)).tolist()
            rows.append(dict(
                p=[float(sample["p"][0]), float(sample["p"][1])],
                tangent=[float(tangent[0]), float(tangent[1])],
                speed=float(sample.get("speed", 0.0)),
                on_circle=phase["name"] == "rail",
                circle=phase.get("center"),
            ))
    cleaned = [rows[0]]
    for row in rows[1:]:
        if abs(row["p"][0] - cleaned[-1]["p"][0]) + abs(row["p"][1] - cleaned[-1]["p"][1]) > 1e-4:
            cleaned.append(row)
    return cleaned


def _scales(index, count):
    frac = index / max(count - 1, 1)
    bank = float(np.sin(np.pi * np.clip((frac - 0.12) / 0.7, 0.0, 1.0)) ** 1.2)
    opening = float(np.clip((frac - 0.82) / 0.18, 0.0, 1.0))
    opening = opening * opening * (3.0 - 2.0 * opening)
    return bank, 1.0 - opening


def _box(origin, axis_u, axis_v, axis_w, hu, hv, hw):
    corners = []
    for su in (-1.0, 1.0):
        for sv in (-1.0, 1.0):
            for sw in (-1.0, 1.0):
                corners.append(origin + axis_u * su * hu + axis_v * sv * hv + axis_w * sw * hw)
    # faces as quads of the 8 corners in su,sv,sw order:
    # 0 ---, 1 --+, 2 -+-, 3 -++, 4 +--, 5 +-+, 6 ++-, 7 +++
    quads = (
        (0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4),
        (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5),
    )
    return corners, quads


def build_channel(guide, marble_radius=MARBLE_RADIUS):
    rows = centerline_from_guide(guide)
    verts, faces = [], []
    probes = {"floor": [], "wall": [], "bracket": []}
    stations = []
    distance = 0.0
    next_bracket = 0.15
    count = len(rows)
    for i, row in enumerate(rows):
        point = np.array([row["p"][0], 0.0, row["p"][1]])
        if row["on_circle"] and row["circle"] is not None:
            center = np.array([row["circle"][0], 0.0, row["circle"][1]])
            normal = _unit(center - point)
        else:
            normal = _up_normal(row["tangent"])
        tangent = _unit([row["tangent"][0], 0.0, row["tangent"][1]])
        lateral = _unit(np.cross(tangent, normal))
        if lateral[1] < 0:
            lateral = -lateral
        bank, open_scale = _scales(i, count)
        floor = point - normal * marble_radius
        inner_h = (WALL_INNER + 0.02 * bank) * open_scale
        outer_h = (WALL_OUTER + 0.08 * bank) * open_scale
        hw = HALF_WIDTH
        profile = [
            floor - lateral * hw,
            floor + lateral * hw,
            floor - lateral * hw + normal * inner_h,
            floor + lateral * hw + normal * outer_h,
            floor - lateral * hw - normal * FLOOR_THICK,
            floor + lateral * hw - normal * FLOOR_THICK,
        ]
        base = len(verts)
        for vertex in profile:
            verts.append([float(v) for v in vertex])
        probes["floor"].append([float(v) for v in floor])
        if inner_h > 0.012:
            probes["wall"].append([float(v) for v in (floor - lateral * hw + normal * inner_h * 0.55)])
        if outer_h > 0.012:
            probes["wall"].append([float(v) for v in (floor + lateral * hw + normal * outer_h * 0.55)])
        if i:
            prev = base - 6
            for a, b in ((0, 1), (4, 5), (0, 4), (1, 5), (0, 2), (1, 3)):
                # Wall tops only connect when both stations still have a wall.
                if a in (2, 3) or b in (2, 3):
                    if inner_h <= 0.012 and a in (0, 2) and b in (0, 2):
                        continue
                faces.append([prev + a, prev + b, base + b, base + a])
            step = float(np.linalg.norm(point - np.array([rows[i - 1]["p"][0], 0.0, rows[i - 1]["p"][1]])))
            distance += step
            if distance >= next_bracket and open_scale > 0.4:
                _bracket(floor, normal, lateral, verts, faces, probes["bracket"])
                next_bracket = distance + BRACKET_EVERY
        stations.append(dict(
            center=[float(point[0]), 0.0, float(point[2])],
            floor=[float(floor[0]), float(floor[1]), float(floor[2])],
            normal=[float(normal[0]), float(normal[1]), float(normal[2])],
            bank=bank, wall_open=open_scale, inner_h=float(inner_h), outer_h=float(outer_h),
        ))
    return dict(
        verts=verts, faces=faces, probes=probes, stations=stations,
        marble_radius_m=marble_radius, half_width_m=HALF_WIDTH,
        material="jewelbox_satin_brass",
        support_material="jewelbox_satin_brass_bracket",
        principles=[
            "US5007876A: banked hairpin, outer guide higher through the reversal.",
            "US4874342A: downhill speed run, upturned lip, free trajectory after the lip.",
        ],
        not_a_manufactured_replica=True,
    )


def _bracket(floor, normal, lateral, verts, faces, probes):
    start = np.asarray(floor, float) - np.asarray(normal, float) * (FLOOR_THICK + 0.006)
    end = np.array([start[0], WALL_Y_TARGET, start[2]])
    axis = end - start
    length = float(np.linalg.norm(axis))
    if length < 0.04:
        return
    axis = axis / length
    side = lateral if abs(float(np.dot(lateral, axis))) < 0.8 else _unit(np.cross(axis, normal))
    up = _unit(np.cross(side, axis))
    base = len(verts)
    corners, quads = _box(0.5 * (start + end), side, up, axis, 0.011, 0.011, length * 0.5)
    for corner in corners:
        verts.append([float(v) for v in corner])
        probes.append([float(v) for v in corner])
    for quad in quads:
        faces.append([base + k for k in quad])
    foot_base = len(verts)
    foot_corners, foot_quads = _box(end + axis * 0.006, side, up, axis, 0.038, 0.038, 0.006)
    for corner in foot_corners:
        verts.append([float(v) for v in corner])
        probes.append([float(v) for v in corner])
    for quad in foot_quads:
        faces.append([foot_base + k for k in quad])
