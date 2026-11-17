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


def _quad_area(verts, quad):
    q = [np.asarray(verts[i], float) for i in quad]
    n1 = np.cross(q[1] - q[0], q[2] - q[0])
    n2 = np.cross(q[2] - q[0], q[3] - q[0])
    return 0.5 * (float(np.linalg.norm(n1)) + float(np.linalg.norm(n2)))


def _bowtie(verts, quad):
    """True when the quad's two triangles face opposite ways."""
    q = [np.asarray(verts[i], float) for i in quad]
    n1 = np.cross(q[1] - q[0], q[2] - q[0])
    n2 = np.cross(q[2] - q[0], q[3] - q[0])
    return float(np.dot(n1, n2)) < 0.0


def _orient_normals(rows, normals):
    """Keep the floor on one side of the marble.

    The circle normal points at the centre of curvature, so the floor sits
    outside the turn. The straight capture used to pick the opposite sign, and
    the one quad at that join cut through the ball.
    """
    normals = [np.array(n, float) for n in normals]
    circle = [i for i, row in enumerate(rows) if row.get("on_circle")]
    if circle:
        # The first circle sample keeps the curvature normal. Everything else
        # matches its neighbour so the floor cannot jump through the ball.
        anchor = circle[0]
        for i in range(anchor + 1, len(normals)):
            if float(np.dot(normals[i], normals[i - 1])) < 0.0:
                normals[i] = -normals[i]
        for i in range(anchor - 1, -1, -1):
            if float(np.dot(normals[i], normals[i + 1])) < 0.0:
                normals[i] = -normals[i]
    else:
        for i in range(1, len(normals)):
            if float(np.dot(normals[i], normals[i - 1])) < 0.0:
                normals[i] = -normals[i]
    return normals


def build_channel(guide, marble_radius=MARBLE_RADIUS):
    rows = centerline_from_guide(guide)
    raw = []
    for row in rows:
        point = np.array([row["p"][0], 0.0, row["p"][1]])
        if row["on_circle"] and row["circle"] is not None:
            center = np.array([row["circle"][0], 0.0, row["circle"][1]])
            raw.append(_unit(center - point))
        else:
            raw.append(_up_normal(row["tangent"]))
    normals = _orient_normals(rows, raw)
    verts, faces = [], []
    bracket_faces = []
    probes = {"floor": [], "wall": [], "bracket": []}
    stations = []
    profile_at = []
    distance = 0.0
    next_bracket = 0.15
    count = len(rows)
    for i, row in enumerate(rows):
        point = np.array([row["p"][0], 0.0, row["p"][1]])
        normal = normals[i]
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
        profile_at.append(len(verts))
        base = profile_at[-1]
        for vertex in profile:
            verts.append([float(v) for v in vertex])
        probes["floor"].append([float(v) for v in floor])
        if inner_h > 0.012:
            probes["wall"].append([float(v) for v in (floor - lateral * hw + normal * inner_h * 0.55)])
        if outer_h > 0.012:
            probes["wall"].append([float(v) for v in (floor + lateral * hw + normal * outer_h * 0.55)])
        if i:
            prev = profile_at[-2]
            prev_station = stations[-1]
            for a, b in ((0, 1), (4, 5), (0, 4), (1, 5), (0, 2), (1, 3)):
                # A wall that has already tapered off must not leave a
                # zero-area quad coplanar with the floor. Those flicker.
                if (a, b) == (0, 2) and (inner_h < 0.02 or prev_station["inner_h"] < 0.02):
                    continue
                if (a, b) == (1, 3) and (outer_h < 0.02 or prev_station["outer_h"] < 0.02):
                    continue
                quad = [prev + a, prev + b, base + b, base + a]
                if _quad_area(verts, quad) < 1e-6 or _bowtie(verts, quad):
                    continue
                faces.append(quad)
            step = float(np.linalg.norm(point - np.array([rows[i - 1]["p"][0], 0.0, rows[i - 1]["p"][1]])))
            distance += step
            if distance >= next_bracket and open_scale > 0.4:
                # Outer rim is past the marble (half-width 0.195, radius 0.15), then the wall.
                _bracket(floor + lateral * HALF_WIDTH, normal, lateral, verts, bracket_faces, probes["bracket"])
                next_bracket = distance + BRACKET_EVERY
        stations.append(dict(
            center=[float(point[0]), 0.0, float(point[2])],
            floor=[float(floor[0]), float(floor[1]), float(floor[2])],
            normal=[float(normal[0]), float(normal[1]), float(normal[2])],
            bank=bank, wall_open=open_scale, inner_h=float(inner_h), outer_h=float(outer_h),
        ))
    bracket_face_start = len(faces)
    faces.extend(bracket_faces)
    return dict(
        verts=verts, faces=faces, probes=probes, stations=stations,
        bracket_face_start=bracket_face_start,
        marble_radius_m=marble_radius, half_width_m=HALF_WIDTH,
        material="jewelbox_satin_brass",
        support_material="jewelbox_satin_brass_bracket",
        principles=[
            "US5007876A: banked hairpin, outer guide higher through the reversal.",
            "US4874342A: downhill speed run, upturned lip, free trajectory after the lip.",
        ],
        not_a_manufactured_replica=True,
    )


def _point_tri_distance(point, a, b, c):
    ab = b - a
    ac = c - a
    ap = point - a
    d1 = float(np.dot(ab, ap))
    d2 = float(np.dot(ac, ap))
    if d1 <= 0.0 and d2 <= 0.0:
        return float(np.linalg.norm(ap))
    bp = point - b
    d3 = float(np.dot(ab, bp))
    d4 = float(np.dot(ac, bp))
    if d3 >= 0.0 and d4 <= d3:
        return float(np.linalg.norm(bp))
    vc = d1 * d4 - d3 * d2
    if vc <= 0.0 and d1 >= 0.0 and d3 <= 0.0:
        v = d1 / (d1 - d3)
        return float(np.linalg.norm(point - (a + v * ab)))
    cp = point - c
    d5 = float(np.dot(ab, cp))
    d6 = float(np.dot(ac, cp))
    if d6 >= 0.0 and d5 <= d6:
        return float(np.linalg.norm(cp))
    vb = d5 * d2 - d1 * d6
    if vb <= 0.0 and d2 >= 0.0 and d6 <= 0.0:
        w = d2 / (d2 - d6)
        return float(np.linalg.norm(point - (a + w * ac)))
    va = d3 * d6 - d5 * d4
    if va <= 0.0 and (d4 - d3) >= 0.0 and (d5 - d6) >= 0.0:
        w = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        return float(np.linalg.norm(point - (b + w * (c - b))))
    denom = 1.0 / (va + vb + vc)
    v = vb * denom
    w = vc * denom
    return float(np.linalg.norm(point - (a + ab * v + ac * w)))


def mesh_clearance(channel, radius=MARBLE_RADIUS):
    """Distance from each station centre to the triangle mesh.

    The roll touches the floor at ``radius``. A smaller distance means a
    triangle cuts through the marble (a flipped floor or a bowtie), which is
    not the intended contact.
    """
    verts = np.asarray(channel["verts"], float)
    tris = []
    for face in channel["faces"]:
        if len(face) == 4:
            tris.append((face[0], face[1], face[2]))
            tris.append((face[0], face[2], face[3]))
        elif len(face) >= 3:
            tris.append((face[0], face[1], face[2]))
    gaps = []
    bowties = 0
    for face in channel["faces"]:
        if len(face) != 4:
            continue
        if _bowtie(channel["verts"], face):
            bowties += 1
    for station in channel["stations"]:
        centre = np.asarray(station["center"], float)
        best = min(_point_tri_distance(centre, verts[i], verts[j], verts[k]) for i, j, k in tris)
        gaps.append(best)
    return dict(min_m=float(min(gaps)), median_m=float(np.median(gaps)), bowties=bowties)


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
