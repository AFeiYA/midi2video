"""steel drums v5: chrome rim bar (struck) on top of a round steel pan seen face-on behind the marble plane, with a hammered centre note and six dimpled note areas outlined by grooves."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
def build(C, variant=None):
    rim = C.prim('cube', 0, loc=(0,0,0.025), scale=(0.62,0.12,0.04), bevel=0.015)
    hooks = [C.prim('cube', 2, loc=(x,0.11,0.0), scale=(0.025,0.14,0.04)) for x in (-0.2,0.2)]
    R0, zc, yf = 0.30, -0.28, 0.17                       # pan radius, centre z, front-face y
    pan = C.prim('cyl', 1, loc=(0,yf+0.045,zc), rot=(math.pi/2,0,0), scale=(R0,R0,0.09), bevel=0.012, verts=72)
    C.cut(pan, C.prim('cyl', 1, loc=(0,yf-0.02,zc), rot=(math.pi/2,0,0), scale=(R0-0.03,R0-0.03,0.07), verts=72))   # dish
    ring = C.prim('torus', 1, loc=(0,yf,zc), rot=(math.pi/2,0,0), scale=(R0-0.012,0.014), verts=72)
    notes = [C.prim('sphere', 1, loc=(0,yf+0.02,zc), scale=(0.1,0.018,0.085), verts=40),
             C.prim('torus', 2, loc=(0,yf+0.018,zc), rot=(math.pi/2,0,0), scale=(0.105,0.005), verts=48)]
    for k in range(6):
        t = k*math.pi/3 + 0.3; x = 0.185*math.cos(t); z = zc + 0.175*math.sin(t)
        notes.append(C.prim('sphere', 1, loc=(x,yf+0.02,z), scale=(0.06,0.014,0.05), verts=32))
        notes.append(C.prim('torus', 2, loc=(x,yf+0.018,z), rot=(math.pi/2,0,0), scale=(0.062,0.004), verts=32))
    return [rim, pan, ring] + hooks + notes
