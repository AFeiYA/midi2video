"""flute: procedural striker. Sterling-silver flute body segment (tube, top flush with contact face) with five key cups with cream leather pads on the camera side, a key rod, and joint ferrule rings at both ends; held by two posts to the wall."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    r = 0.05; zc = 0.045 - r
    tube = C.prim('cyl', 0, loc=(0,0,zc), rot=(0,math.pi/2,0), scale=(r,r,0.62), verts=48)
    C.cut(tube, C.prim('cyl', 2, loc=(0.31,0,zc), rot=(0,math.pi/2,0), scale=(0.04,0.04,0.06), verts=32))
    rings = [C.prim('cyl', 2, loc=(x,0,zc), rot=(0,math.pi/2,0), scale=(0.055,0.055,0.022), bevel=0.004, verts=48) for x in (-0.3,0.295)]
    cups = []
    for x in (-0.2,-0.1,0.0,0.1,0.2):
        cups.append(C.prim('cyl', 2, loc=(x,-0.052,zc), rot=(math.pi/2,0,0), scale=(0.026,0.026,0.012), bevel=0.003, verts=32))
        cups.append(C.prim('cyl', 1, loc=(x,-0.0585,zc), rot=(math.pi/2,0,0), scale=(0.019,0.019,0.004), verts=32))
    rod = C.prim('cyl', 2, loc=(0,-0.046,zc-0.036), rot=(0,math.pi/2,0), scale=(0.006,0.006,0.56), verts=12)
    return [tube, rod] + rings + cups
