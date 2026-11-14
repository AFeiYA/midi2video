"""flute v8: a wooden recorder-style flute standing perpendicular to the wall
(axis along local +Y, the wall-normal). The marble hits the tube body itself.
A shallow flattened facet on top of the tube keeps the contact plane at z=+0.045
with +Z normal. Cream/ivory rings, a flared cream bell toward the camera, a cream
foot at the wall, and finger holes cut into the top of the shaft.
"""
import math

def build(C, variant=None):
    # r slightly above 0.045 so a shallow cut at z=0.045 leaves a flat contact facet.
    r = 0.055
    zc = -0.008          # natural top = zc+r = 0.047; flattened to 0.045
    y_bell = -0.80       # cream bell toward the camera (in front of the marble)
    y_join = -0.66       # bell meets the wooden body
    y_foot = 0.278       # cream foot near the wall (wall at y=0.30)

    length = y_foot - y_join
    tube = C.prim('cyl', 0, loc=(0, 0.5 * (y_join + y_foot), zc),
                  rot=(math.pi / 2, 0, 0), scale=(r, r, length), verts=48)
    # Flatten a short contact region around y=0 so the bounce plane is z=+0.045.
    C.cut(tube, C.prim('cube', 0, loc=(0, 0, 0.095), scale=(0.16, 0.24, 0.10)))

    ivory = 1
    dark = 2

    # Bore open toward the camera, through the bell and the front of the body,
    # stopping short of the contact facet.
    bore_cut = C.prim('cyl', dark, loc=(0, 0.5 * (y_bell - 0.02 + -0.16), zc),
                      rot=(math.pi / 2, 0, 0),
                      scale=(0.030, 0.030, (-0.16) - (y_bell - 0.02)), verts=32)

    # --- cream bell, flared toward -Y (camera) ---
    bell_parts = []
    for y, rr, d in (
        (y_join - 0.01, 0.056, 0.03),
        (-0.70, 0.064, 0.06),
        (-0.75, 0.076, 0.05),
        (-0.79, 0.086, 0.03),
    ):
        p = C.prim('cyl', ivory, loc=(0, y, zc), rot=(math.pi / 2, 0, 0),
                   scale=(rr, rr, d), verts=48)
        C.cut(p, C.prim('cyl', dark, loc=(0, y, zc), rot=(math.pi / 2, 0, 0),
                        scale=(0.030, 0.030, d + 0.04), verts=32))
        bell_parts.append(p)
    lip = C.prim('torus', ivory, loc=(0, y_bell, zc), rot=(math.pi / 2, 0, 0),
                 scale=(0.082, 0.009), verts=48)
    C.cut(lip, C.prim('cyl', dark, loc=(0, y_bell, zc), rot=(math.pi / 2, 0, 0),
                      scale=(0.074, 0.074, 0.04), verts=32))
    bore_vis = C.prim('cyl', dark, loc=(0, -0.73, zc), rot=(math.pi / 2, 0, 0),
                      scale=(0.030, 0.030, 0.16), verts=32)

    C.cut(tube, bore_cut)

    # --- ivory rings (out of the contact slab) ---
    rings = []
    for y, rr, d in (
        (-0.64, r * 1.16, 0.022),   # bell joint, in front of the slab
        (-0.22, r * 1.14, 0.020),   # just in front of the marble slab
        (0.18,  r * 1.14, 0.020),   # backplate, toward the wall
        (0.255, r * 1.16, 0.018),   # foot joint
    ):
        rings.append(C.prim('cyl', ivory, loc=(0, y, zc), rot=(math.pi / 2, 0, 0),
                            scale=(rr, rr, d), bevel=0.003, verts=48))

    foot = C.prim('cyl', ivory, loc=(0, 0.292, zc), rot=(math.pi / 2, 0, 0),
                  scale=(r * 1.18, r * 1.18, 0.018), verts=48)
    cap = C.prim('sphere', ivory, loc=(0, 0.300, zc), scale=(r * 1.12, 0.010, r * 1.12), verts=24)

    # --- finger holes cut into the top of the shaft (camera side of the contact) ---
    holes = []
    for y in (-0.58, -0.52, -0.46, -0.40, -0.34, -0.28):
        cutter = C.prim('cyl', dark, loc=(0, y, zc + r), scale=(0.013, 0.013, 0.05), verts=16)
        C.cut(tube, cutter)
        holes.append(C.prim('cyl', dark, loc=(0, y, zc + r - 0.012),
                            scale=(0.012, 0.012, 0.016), verts=16))

    return [tube, lip, bore_vis, foot, cap] + bell_parts + rings + holes
