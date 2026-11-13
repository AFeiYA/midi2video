"""flute v4: larger silver body (r 0.065), gold-plated key cups with dark pads, gold rod, embouchure lip plate ring."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    r = 0.065; zc = 0.045 - r
    tube = C.prim('cyl', 0, loc=(0,0,zc), rot=(0,math.pi/2,0), scale=(r,r,0.62), verts=48)
    C.cut(tube, C.prim('cyl', 1, loc=(0.31,0,zc), rot=(0,math.pi/2,0), scale=(0.05,0.05,0.06), verts=32))
    rings = [C.prim('cyl', 2, loc=(x,0,zc), rot=(0,math.pi/2,0), scale=(0.071,0.071,0.026), bevel=0.004, verts=48) for x in (-0.297,0.292)]
    cups = []
    for x in (-0.21,-0.105,0.0,0.105,0.21):
        cups.append(C.prim('cyl', 2, loc=(x,-0.068,zc), rot=(math.pi/2,0,0), scale=(0.034,0.034,0.014), bevel=0.004, verts=32))
        cups.append(C.prim('cyl', 1, loc=(x,-0.0755,zc), rot=(math.pi/2,0,0), scale=(0.024,0.024,0.004), verts=32))
    rod = C.prim('cyl', 2, loc=(0,-0.058,zc-0.048), rot=(0,math.pi/2,0), scale=(0.008,0.008,0.56), verts=12)
    return [tube, rod] + rings + cups
