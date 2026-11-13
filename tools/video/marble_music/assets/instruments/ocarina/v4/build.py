"""ocarina v4: saturated celadon, 4 larger finger holes on the camera-facing flank, each with a dark inner bore."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    a, b, c, zc = 0.27, 0.15, 0.085, 0.045-0.085
    body = C.prim('sphere', 0, loc=(0,0,zc), scale=(a,b,c), verts=64)
    mouth = C.prim('cube', 0, loc=(0.25,0,zc+0.005), scale=(0.12,0.09,0.06), bevel=0.025)
    for x in (-0.18,-0.09,0.09,0.18):
        y = -0.105; z = zc + c*math.sqrt(max(0.0, 1-(x/a)**2-(y/b)**2))
        C.cut(body, C.prim('sphere', 1, loc=(x,y,z), scale=(0.036,0.036,0.036), verts=24))
    C.cut(mouth, C.prim('cube', 1, loc=(0.31,0,zc+0.012), scale=(0.02,0.05,0.014)))
    return [body, mouth]
