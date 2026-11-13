"""flute v7: a thin silver flute stands perpendicular to the wall (axis along local +Y, the
wall-normal) and acts as the mount. The hit surface is a small wooden striker board, same
planner size/angle as before (0.62 x 0.09 face, top at z=+0.045), mounted on the flute's
front end so the contact point stays at the origin.
Keys/holes sit on the tube in the backplate zone (y>=0.16) so they stay out of the marble path.
No side pins — the flute itself is the support, otherwise two dark legs hide the post.
"""
import math

def build(C, variant=None):
    # Small striker board: planner rectangle, modest Y depth. Slot 0 = body (flashes on hit).
    board = C.prim('cube', 0, loc=(0, 0, 0), scale=(0.62, 0.11, 0.09), bevel=0.012)

    # Thin post along +Y (into the wall). Board occupies y in [-0.055, 0.055].
    r = 0.040
    zc = 0.0
    y0, y1 = 0.052, 0.286
    length = y1 - y0
    yc = 0.5 * (y0 + y1)
    tube = C.prim('cyl', 1, loc=(0, yc, zc), rot=(math.pi / 2, 0, 0), scale=(r, r, length), verts=48)

    # Ferrule at the board; mid joint; a clear wall flange + crown so the far end reads from a face-on camera.
    ferrule = C.prim('cyl', 3, loc=(0, y0 + 0.008, zc), rot=(math.pi / 2, 0, 0),
                     scale=(r * 1.20, r * 1.20, 0.018), bevel=0.002, verts=48)
    midring = C.prim('cyl', 3, loc=(0, 0.20, zc), rot=(math.pi / 2, 0, 0),
                     scale=(r * 1.12, r * 1.12, 0.012), bevel=0.002, verts=32)
    flange = C.prim('cyl', 1, loc=(0, 0.298, zc), rot=(math.pi / 2, 0, 0),
                    scale=(0.055, 0.055, 0.008), bevel=0.002, verts=48)
    cap = C.prim('cyl', 3, loc=(0, y1 - 0.004, zc), rot=(math.pi / 2, 0, 0),
                 scale=(r * 1.25, r * 1.25, 0.016), verts=48)
    crown = C.prim('sphere', 3, loc=(0, y1 + 0.004, zc), scale=(r * 1.15, 0.012, r * 1.15), verts=24)

    def radial(az, extra, y):
        return ((r + extra) * math.cos(az), y, zc + (r + extra) * math.sin(az))

    # Lip plate + embouchure on the underside (the side that peeks under the board).
    lip_az = -0.55 * math.pi
    lx, ly, lz = radial(lip_az, 0.008, 0.172)
    lip = C.prim('sphere', 1, loc=(lx, ly, lz), scale=(0.024, 0.016, 0.014), verts=24)
    hx, hy, hz = radial(lip_az, 0.014, 0.172)
    hole = C.prim('sphere', 2, loc=(hx, hy, hz), scale=(0.010, 0.008, 0.008), verts=16)

    rod_az = -0.40 * math.pi
    rx, _, rz = radial(rod_az, 0.006, 0.0)
    rod = C.prim('cyl', 3, loc=(rx, 0.225, rz), rot=(math.pi / 2, 0, 0),
                 scale=(0.005, 0.005, 0.14), verts=12)

    cups, pads, tone = [], [], []
    # Larger gold cups, mostly on the underside / sides so they read from the elevated camera.
    keys = [
        (0.162, -0.55 * math.pi),
        (0.182, -0.25 * math.pi),
        (0.202, -0.70 * math.pi),
        (0.222,  0.10 * math.pi),
        (0.242, -0.45 * math.pi),
        (0.262, -0.85 * math.pi),
        (0.278, -0.20 * math.pi),
    ]
    for yk, az in keys:
        cx, _, cz = radial(az, 0.010, yk)
        cups.append(C.prim('cyl', 3, loc=(cx, yk, cz), rot=(0, math.pi / 2 - az, 0),
                           scale=(0.018, 0.018, 0.012), bevel=0.002, verts=24))
        px, _, pz = radial(az, 0.018, yk)
        pads.append(C.prim('cyl', 2, loc=(px, yk, pz), rot=(0, math.pi / 2 - az, 0),
                           scale=(0.012, 0.012, 0.004), verts=16))

    for yk, az in ((0.175, 0.45 * math.pi), (0.215, 0.60 * math.pi), (0.255, 0.35 * math.pi)):
        tx, _, tz = radial(az, 0.002, yk)
        tone.append(C.prim('sphere', 2, loc=(tx, yk, tz), scale=(0.009, 0.007, 0.009), verts=16))

    return [board, tube, ferrule, midring, flange, cap, crown, lip, hole, rod] + cups + pads + tone
