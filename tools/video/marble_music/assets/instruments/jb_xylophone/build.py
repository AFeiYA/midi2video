"""jb_xylophone (jewelbox 10): pitch-rainbow bar + rainbow xylophone icon (graded bars on maple rails, crossed mallets)."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def build(C, variant=None):
    P = [C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.014)]
    for x in (-0.2, 0.2): P.append(C.prim('sphere', 4, loc=(x,-0.0,0.04), scale=(0.018,0.018,0.005), verts=12))   # nail heads (flush)
    # rainbow icon below: 8 graded bars (vertical in the icon), maple rails behind them
    n = 8; X = [-0.42 + 0.84*i/(n-1) for i in range(n)]
    def railz(x, top): return (-0.11 if top else -0.43 + 0.16*(x+0.46)/0.92)
    for top in (True, False):
        za, zb = railz(-0.48, top), railz(0.48, top); L = math.hypot(0.96, zb-za)
        P.append(C.prim('cube', 1, loc=(0,0.245,(za+zb)/2), rot=(0,-math.atan2(zb-za,0.96),0), scale=(L,0.05,0.04), bevel=0.01))
    for i, x in enumerate(X):
        z0, z1 = railz(x, True) + 0.035, railz(x, False) - 0.035
        P.append(C.prim('cube', 2 + (i % 2), loc=(x,0.20,(z0+z1)/2), scale=(0.085,0.03,z0-z1), bevel=0.01))
        for z in (railz(x, True), railz(x, False)): P.append(C.prim('sphere', 4, loc=(x,0.183,z), scale=(0.011,0.006,0.011), verts=10))
    # crossed mallets in front of the icon
    for a, b in (((-0.30,-0.50), (0.20,-0.24)), ((0.30,-0.50), (-0.20,-0.24))):
        L = math.hypot(b[0]-a[0], b[1]-a[1])
        P.append(C.prim('cyl', 1, loc=((a[0]+b[0])/2,0.175,(a[1]+b[1])/2), rot=(0,math.atan2(b[0]-a[0],b[1]-a[1]),0), scale=(0.008,0.008,L), verts=10))
        P.append(C.prim('sphere', 5, loc=(b[0],0.18,b[1]), scale=(0.024,0.022,0.024), verts=16))
    return P
