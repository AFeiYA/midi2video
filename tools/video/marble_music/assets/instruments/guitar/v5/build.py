"""guitar v5: six black strings (struck, flush with the contact face) over a sunburst guitar BODY seen face-on behind the marble plane - lower and upper bouts, waist, sound hole with rosette, bridge - plus fingerboard neck and headstock with tuning pegs."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
def build(C, variant=None):
    yb = 0.2
    low = C.prim('cyl', 0, loc=(0.12,yb,0.0), rot=(math.pi/2,0,0), scale=(0.22,0.22,0.06), bevel=0.012, verts=72)
    up  = C.prim('cyl', 0, loc=(-0.18,yb,0.0), rot=(math.pi/2,0,0), scale=(0.17,0.17,0.06), bevel=0.012, verts=72)
    waist = C.prim('cube', 0, loc=(-0.04,yb,0.0), scale=(0.2,0.06,0.26), bevel=0.01)
    C.cut(up, C.prim('cyl', 3, loc=(-0.12,yb-0.05,0.0), rot=(math.pi/2,0,0), scale=(0.068,0.068,0.08), verts=48))
    ros = C.prim('torus', 4, loc=(-0.12,yb-0.031,0.0), rot=(math.pi/2,0,0), scale=(0.084,0.01), verts=64)
    bind = [C.prim('torus', 4, loc=(cx,yb-0.031,0.0), rot=(math.pi/2,0,0), scale=(r0,0.006), verts=72) for cx, r0 in ((0.12,0.22),(-0.18,0.17))]
    bridge = C.prim('cube', 2, loc=(0.2,0.04,0.02), scale=(0.07,0.30,0.03), bevel=0.006)          # in the slab, inside the contact rectangle
    saddle = C.prim('cube', 4, loc=(0.2,0.0,0.036), scale=(0.01,0.24,0.006))
    nut = C.prim('cube', 4, loc=(-0.305,0.04,0.02), scale=(0.012,0.30,0.03))
    neck = C.prim('cube', 2, loc=(-0.47,yb-0.005,0.0), scale=(0.36,0.05,0.075), bevel=0.008)
    frets = [C.prim('cube', 5, loc=(x,yb-0.032,0.0), scale=(0.006,0.006,0.085)) for x in (-0.36,-0.41,-0.46,-0.51,-0.56,-0.61)]
    head = C.prim('cube', 2, loc=(-0.71,yb,0.0), scale=(0.13,0.05,0.11), bevel=0.02)
    pegs = [C.prim('cyl', 5, loc=(x,yb-0.03,s*0.07), rot=(0,0,0), scale=(0.014,0.014,0.05), verts=12) for x in (-0.675,-0.71,-0.745) for s in (-1,1)]
    strings = []
    for i, y in enumerate((-0.095,-0.057,-0.019,0.019,0.057,0.095)):
        r = 0.0135 - 0.0009*i
        strings.append(C.prim('cyl', 1, loc=(0.0,y,0.045-r), rot=(0,math.pi/2,0), scale=(r,r,0.62), verts=12))
    return [low, up, waist, ros, bridge, saddle, nut, neck, head] + bind + frets + pegs + strings
