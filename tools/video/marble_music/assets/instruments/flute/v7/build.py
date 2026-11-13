"""flute v7: one continuous silver flute at the striker angle (short head + body + short foot in the same plane).
The tube itself is the hit surface — top flush with z=+0.045. Head/foot are kept short so they stay out of the marble path."""
import math
def build(C, variant=None):
    r = 0.065
    zc = 0.045 - r
    tube = C.prim('cyl', 0, loc=(0, 0, zc), rot=(0, math.pi/2, 0), scale=(r, r, 0.62), verts=48)
    # short head / foot: keep-out failed at |x|≈0.47, so both ends stay inside ~0.38
    head = C.prim('cyl', 0, loc=(-0.318, 0, zc), rot=(0, math.pi/2, 0), scale=(r * 0.94, r * 0.94, 0.016), verts=48)
    foot = C.prim('cyl', 0, loc=(0.345, 0, zc), rot=(0, math.pi/2, 0), scale=(r * 0.94, r * 0.94, 0.07), verts=48)
    rings = [C.prim('cyl', 2, loc=(x, 0, zc), rot=(0, math.pi/2, 0), scale=(0.071, 0.071, 0.018), bevel=0.003, verts=48)
             for x in (-0.310, 0.310, -0.297, 0.292)]
    crown = C.prim('sphere', 2, loc=(-0.318, 0, zc), scale=(0.010, 0.052, 0.052), verts=24)
    lip = C.prim('sphere', 0, loc=(-0.310, -0.055, zc + 0.032), scale=(0.028, 0.022, 0.014), verts=32)
    hole = C.prim('sphere', 1, loc=(-0.310, -0.060, zc + 0.044), scale=(0.012, 0.009, 0.009), verts=20)
    cups, pads = [], []
    for x in (-0.21, -0.105, 0.0, 0.105, 0.21):
        cups.append(C.prim('cyl', 2, loc=(x, -0.068, zc), rot=(math.pi/2, 0, 0), scale=(0.034, 0.034, 0.014), bevel=0.003, verts=32))
        pads.append(C.prim('cyl', 1, loc=(x, -0.0755, zc), rot=(math.pi/2, 0, 0), scale=(0.024, 0.024, 0.004), verts=32))
    rod = C.prim('cyl', 2, loc=(0, -0.058, zc - 0.048), rot=(0, math.pi/2, 0), scale=(0.008, 0.008, 0.56), verts=12)
    fcap = C.prim('cyl', 2, loc=(0.382, 0, zc), rot=(0, math.pi/2, 0), scale=(r * 0.98, r * 0.98, 0.010), verts=48)
    fkeys = [C.prim('cyl', 2, loc=(x, -0.066, zc), rot=(math.pi/2, 0, 0), scale=(0.026, 0.026, 0.011), verts=24)
             for x in (0.335, 0.365)]
    return [tube, head, foot, rod, crown, lip, hole, fcap] + rings + cups + pads + fkeys
