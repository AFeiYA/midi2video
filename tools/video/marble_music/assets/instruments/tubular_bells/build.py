"""tubular_bells: procedural striker. Polished-brass tubular-bell chime (tube of radius 0.075 lying along the paddle), crown cap ring at the upper end, hollow dark bore at the open end, hung by a cord to the wall."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    r = 0.075; zc = 0.045 - r
    tube = C.prim('cyl', 0, loc=(0,0,zc), rot=(0,math.pi/2,0), scale=(r,r,0.62), verts=48)
    C.cut(tube, C.prim('cyl', 2, loc=(0.31,0,zc), rot=(0,math.pi/2,0), scale=(0.06,0.06,0.10), verts=48))
    cap = C.prim('cyl', 1, loc=(-0.30,0,zc), rot=(0,math.pi/2,0), scale=(0.084,0.084,0.05), bevel=0.01, verts=48)
    cord = C.prim('cyl', 3, loc=(-0.30,0.2,zc), rot=(math.pi/2,0,0), scale=(0.008,0.008,0.22), verts=10)
    return [tube, cap, cord]
