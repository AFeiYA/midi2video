"""jb_vibraphone (jewelbox 08): aluminium bar + neighbour bars, gold resonators (meta.hanging) with fan discs on a motor shaft."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

TUBES = [-0.47, 0.0, 0.47]
def build(C, variant=None):
    P = [C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.016)]
    P += [C.prim('cyl', 1, loc=(x,0.06,0), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.46), verts=12) for x in (-0.14,0.14)]
    for x in (-0.47, 0.47):                                                                          # neighbour bars (behind the marble plane)
        P.append(C.prim('cube', 0 if False else 4, loc=(x,0.2,0.0), scale=(0.26,0.07,0.06), bevel=0.012))
    P.append(C.prim('cube', 3, loc=(0,0.245,-0.035), scale=(1.30,0.05,0.04), bevel=0.008))          # frame rail
    P.append(C.prim('cyl', 4, loc=(0,0.222,-0.09), rot=(0,math.pi/2,0), scale=(0.008,0.008,1.12), verts=12))   # motor shaft
    for x in TUBES:
        P.append(C.prim('cyl', 3, loc=(x,0.222,-0.09), rot=(0,math.pi/2,0), scale=(0.046,0.046,0.006), verts=24))  # fan discs
    P.append(C.prim('cube', 3, loc=(0.62,0.222,-0.10), scale=(0.08,0.07,0.06), bevel=0.01))         # motor box
    P.append(C.prim('cyl', 4, loc=(0.62,0.185,-0.10), rot=(math.pi/2,0,0), scale=(0.015,0.015,0.006), verts=16))
    return P
