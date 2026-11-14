"""marimba v5: arched rosewood bar (struck) + face-on keyboard of seven graded rosewood bars on cords + dark frame rails."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def build(C, variant=None):
    pts = [(-0.31,0.045),(0.31,0.045),(0.31,-0.045)]
    n = 14
    for i in range(n+1):
        x = 0.22 - 0.44*i/n; pts.append((x, -0.045 + 0.038*(1-(x/0.22)**2)))
    pts.append((-0.31,-0.045))
    P = [C.shape_profile('marimba_bar', pts, 0.30, -0.15, 0, bevel=0.012)]
    P += [C.prim('cyl', 1, loc=(x,0.06,-0.015), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.42), verts=12) for x in (-0.14,0.14)]
    nb = 7; w = 0.084; top = -0.06
    for i in range(nb):
        x = -0.30 + w/2 + i*(w+0.0093); L = 0.34 - 0.025*i
        P.append(C.prim('cube', 3, loc=(x,0.19,top-L/2), scale=(w,0.035,L), bevel=0.012))
        for zz in (top-0.22*L, top-0.78*L): P.append(C.prim('sphere', 4, loc=(x,0.17,zz), scale=(0.008,0.006,0.008), verts=10))
    for zf in (0.22, 0.78):   # cords through the bar nodes (follow the graded lengths)
        a = (-0.30+w/2, top-zf*0.34); b = (-0.30+w/2+6*(w+0.0093), top-zf*(0.34-0.15))
        L_ = math.hypot(b[0]-a[0], b[1]-a[1]); ang = math.atan2(b[0]-a[0], b[1]-a[1])
        P.append(C.prim('cyl', 1, loc=((a[0]+b[0])/2,0.168,(a[1]+b[1])/2), rot=(0,ang,0), scale=(0.004,0.004,L_+0.1), verts=8))
    P.append(C.prim('cube', 2, loc=(-0.335,0.22,-0.22), scale=(0.03,0.05,0.36), bevel=0.008))
    P.append(C.prim('cube', 2, loc=(0.335,0.22,-0.17), scale=(0.03,0.05,0.26), bevel=0.008))
    return P
