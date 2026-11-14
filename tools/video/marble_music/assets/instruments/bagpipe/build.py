"""bagpipe (hook50 08): blackwood drone (struck) on a tartan bag with two tall drones, chanter and cords."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def pipe(C, a, b, r, mi):
    ax, az = a; bx, bz = b; L = math.hypot(bx-ax, bz-az); ang = math.atan2(bx-ax, bz-az)
    return C.prim('cyl', mi, loc=((ax+bx)/2, 0.24, (az+bz)/2), rot=(0, ang, 0), scale=(r, r, L), verts=20)
def build(C, variant=None):
    P = [C.prim('cyl', 0, loc=(0,0,0.0), rot=(0,math.pi/2,0), scale=(0.045,0.045,0.62), verts=40)]
    for x in (-0.27,-0.09,0.09,0.27): P.append(C.prim('cyl', 2, loc=(x,0,0.0), rot=(0,math.pi/2,0), scale=(0.0452,0.0452,0.03), verts=40))
    P.append(C.prim('sphere', 1, loc=(0.02,0.215,-0.21), scale=(0.29,0.06,0.19), verts=48))          # tartan bag
    # two tall drones rising up-left behind, ivory tops
    for (a, b, r) in (((-0.12,-0.06),(-0.42,0.36),0.03), ((-0.02,-0.05),(-0.26,0.44),0.028)):
        P.append(pipe(C, a, b, r, 3))
        P.append(C.prim('cyl', 2, loc=(b[0],0.24,b[1]), rot=(0, math.atan2(b[0]-a[0], b[1]-a[1]), 0), scale=(r*1.5, r*1.5, 0.05), verts=20))
    P.append(pipe(C, (0.2,-0.33), (0.3,-0.62), 0.024, 3))                                             # chanter
    P.append(C.prim('cyl', 2, loc=(0.3,0.24,-0.63), scale=(0.035,0.035,0.04), verts=20))
    P.append(pipe(C, (0.26,-0.1), (0.44,0.06), 0.016, 3))                                             # blowpipe
    for (a, b) in (((-0.3,0.2),(-0.12,-0.08)), ((-0.2,0.26),(-0.04,-0.06))):                          # red cords
        P.append(C.prim('cyl', 4, loc=((a[0]+b[0])/2, 0.17, (a[1]+b[1])/2), rot=(0, math.atan2(b[0]-a[0], b[1]-a[1]), 0), scale=(0.007,0.007,math.hypot(b[0]-a[0], b[1]-a[1])), verts=8))
    P.append(C.prim('sphere', 4, loc=(-0.14,0.16,-0.1), scale=(0.022,0.015,0.035), verts=12))
    return P
