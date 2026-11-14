"""finale (hook50 09): gold bar (struck) + gold star + red bow + two jingle bells."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.0), scale=(0.62,0.16,0.09), bevel=0.02)]
    pts = []
    for i in range(10):
        r = 0.27 if i % 2 == 0 else 0.11; a = math.pi/2 + i*math.pi/5
        pts.append((r*math.cos(a), -0.27 + r*math.sin(a)))
    P.append(C.shape_profile('fin_star', pts, 0.05, 0.2, 1, bevel=0.012))
    # red bow just below the bar
    for s in (-1, 1):
        P.append(C.prim('sphere', 2, loc=(s*0.07,0.17,-0.06), rot=(0, s*0.5, 0), scale=(0.07,0.02,0.04), verts=24))
        P.append(C.prim('cube', 2, loc=(s*0.05,0.172,-0.12), rot=(0, s*0.35, 0), scale=(0.03,0.01,0.11)))
    P.append(C.prim('sphere', 2, loc=(0,0.165,-0.06), scale=(0.028,0.02,0.028), verts=16))
    # jingle bells on cords at both sides
    for s in (-1, 1):
        bx = s*0.36
        P.append(C.prim('cyl', 2, loc=(s*0.33,0.19,-0.07), rot=(0, -s*0.4, 0), scale=(0.006,0.006,0.15), verts=8))
        P.append(C.prim('sphere', 3, loc=(bx,0.2,-0.18), scale=(0.06,0.06,0.06), verts=32))
        P.append(C.prim('cube', 4, loc=(bx,0.14,-0.19), scale=(0.07,0.01,0.008)))
        P.append(C.prim('sphere', 4, loc=(bx,0.143,-0.21), scale=(0.012,0.006,0.012), verts=12))
    return P
