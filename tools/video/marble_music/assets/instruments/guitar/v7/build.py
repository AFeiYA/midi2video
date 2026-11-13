"""guitar v7: tilted acoustic top as the hit surface (body in the striker plane, top toward +Z).
Six strings sit on the top, flush with z=+0.045. The neck rises toward the wall so the headstock
leaves the marble slab (keep-out failed when the headstock stayed at y≈0.03, x≈-0.58)."""
import math
def build(C, variant=None):
    yb, zt, th = 0.07, 0.012, 0.040
    low = C.prim('cyl', 0, loc=(0.14, yb, zt), scale=(0.20, 0.20, th), bevel=0.008, verts=72)
    up  = C.prim('cyl', 0, loc=(-0.14, yb, zt), scale=(0.155, 0.155, th), bevel=0.008, verts=72)
    waist = C.prim('cube', 0, loc=(0.00, yb, zt), scale=(0.24, 0.24, th), bevel=0.008)
    C.cut(up, C.prim('cyl', 3, loc=(-0.11, yb, zt), scale=(0.055, 0.055, 0.08), verts=48))
    ros = C.prim('torus', 4, loc=(-0.11, yb, zt + th / 2 - 0.001), scale=(0.068, 0.007), verts=64)
    bind = [C.prim('torus', 4, loc=(cx, yb, zt + th / 2 - 0.001), scale=(rr, 0.005), verts=72)
            for cx, rr in ((0.14, 0.20), (-0.14, 0.155))]
    strings = []
    for i, y in enumerate((-0.040, -0.024, -0.008, 0.008, 0.024, 0.040)):
        rr = 0.0120 - 0.0007 * i
        strings.append(C.prim('cyl', 1, loc=(0.0, y, 0.045 - rr), rot=(0, math.pi/2, 0), scale=(rr, rr, 0.62), verts=12))
    bridge = C.prim('cube', 2, loc=(0.20, 0.00, 0.036), scale=(0.06, 0.22, 0.016), bevel=0.004)
    saddle = C.prim('cube', 4, loc=(0.20, 0.00, 0.043), scale=(0.010, 0.20, 0.005))
    nut = C.prim('cube', 4, loc=(-0.305, 0.00, 0.038), scale=(0.012, 0.20, 0.016))
    # neck climbs toward the wall ( +Y ): starts near the nut, headstock is behind the marble plane (y>0.16)
    neck = C.prim('cube', 2, loc=(-0.35, 0.19, 0.020), scale=(0.10, 0.06, 0.022), bevel=0.006)
    frets = [C.prim('cube', 5, loc=(x, 0.16, 0.032), scale=(0.005, 0.010, 0.055))
             for x in (-0.33, -0.36, -0.39)]
    head = C.prim('cube', 2, loc=(-0.44, 0.23, 0.022), scale=(0.08, 0.048, 0.075), bevel=0.016)
    pegs = [C.prim('cyl', 5, loc=(x, 0.20, s * 0.045), scale=(0.011, 0.011, 0.030), verts=12)
            for x in (-0.420, -0.445, -0.470) for s in (-1, 1)]
    return [low, up, waist, ros, bridge, saddle, nut, neck, head] + bind + frets + pegs + strings
