"""ocarina v5: larger sweet-potato body (crown flush with contact face) with four big finger holes on the camera-facing face, a protruding mouthpiece with dark windway and labium window (mouthpiece behind the marble plane)."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
def build(C, variant=None):
    a, b, c, zc = 0.27, 0.14, 0.125, 0.045-0.125
    body = C.prim('sphere', 0, loc=(0,0,zc), scale=(a,b,c), verts=64)
    tail = C.prim('sphere', 0, loc=(-0.2,0.02,zc-0.01), scale=(0.11,0.11,0.1), verts=40)
    for x, dz in ((-0.15,0.035),(-0.06,0.045),(0.05,0.045),(0.14,0.03)):
        z = zc + dz; y = -b*math.sqrt(max(0.0, 1-(x/a)**2-(dz/c)**2))
        C.cut(body, C.prim('sphere', 1, loc=(x,y,z), scale=(0.034,0.034,0.034), verts=24))
    mouth = C.prim('cube', 0, loc=(0.32,0.2,zc+0.01), scale=(0.24,0.1,0.075), bevel=0.03)
    C.cut(mouth, C.prim('cube', 1, loc=(0.44,0.2,zc+0.02), scale=(0.03,0.06,0.018)))
    win = C.prim('cube', 1, loc=(0.19,-0.12,zc+0.04), rot=(0,0,0.5), scale=(0.05,0.03,0.035))
    return [body, tail, mouth, win]
