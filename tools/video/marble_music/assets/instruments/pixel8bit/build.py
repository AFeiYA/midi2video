"""pixel8bit (hook50 07): seven pixel blocks (struck) + glowing voxel eighth-note on a dark console plate with d-pad and A/B buttons."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
BITMAP = ['....XXXX..', '....X..XX.', '....X...X.', '....X.....', '....X.....', '..XXX.....', '.XXXX.....', '.XXXX.....', '..XX......']
def build(C, variant=None):
    P = []
    w = 0.62/7
    for i in range(7):
        x = -0.31 + w*(i+0.5)
        P.append(C.prim('cube', 0, loc=(x,0,0.0), scale=(w-0.006,0.20,0.09), bevel=0.008, smooth=False))
        P.append(C.prim('cube', 3, loc=(x,-0.1,0.0), scale=(w*0.42,0.004,0.036), smooth=False))          # lit pixel inset on the front face
    P.append(C.prim('cube', 1, loc=(0,0.24,-0.27), scale=(0.70,0.06,0.48), bevel=0.03))                 # console plate
    s = 0.046
    for r, row in enumerate(BITMAP):
        for c, ch in enumerate(row):
            if ch == 'X': P.append(C.prim('cube', 2, loc=(-0.31 + c*s, 0.195, -0.08 - r*s), scale=(s*0.92,0.04,s*0.92), smooth=False))
    # d-pad + buttons on the right of the plate
    P.append(C.prim('cube', 3, loc=(0.23,0.205,-0.36), scale=(0.09,0.03,0.03), smooth=False))
    P.append(C.prim('cube', 3, loc=(0.23,0.205,-0.36), scale=(0.03,0.03,0.09), smooth=False))
    for x, z in ((0.17,-0.46),(0.27,-0.46)): P.append(C.prim('cyl', 2, loc=(x,0.205,z), rot=(math.pi/2,0,0), scale=(0.028,0.028,0.03), verts=20))
    return P
