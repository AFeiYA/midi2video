"""flute v5: v4 body section (struck) backed by one continuous tube behind the marble plane (head joint with lip plate and crown -> foot joint with keys) so the whole flute reads as a long thin instrument."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
def build(C, variant=None):
    r = 0.065; zc = 0.045 - r
    tube = C.prim('cyl', 0, loc=(0,0,zc), rot=(0,math.pi/2,0), scale=(r,r,0.62), verts=48)
    C.cut(tube, C.prim('cyl', 1, loc=(0.31,0,zc), rot=(0,math.pi/2,0), scale=(0.05,0.05,0.06), verts=32))
    rings = [C.prim('cyl', 2, loc=(x,0,zc), rot=(0,math.pi/2,0), scale=(0.071,0.071,0.026), bevel=0.004, verts=48) for x in (-0.297,0.292)]
    cups = []
    for x in (-0.21,-0.105,0.0,0.105,0.21):
        cups.append(C.prim('cyl', 2, loc=(x,-0.068,zc), rot=(math.pi/2,0,0), scale=(0.034,0.034,0.014), bevel=0.004, verts=32))
        cups.append(C.prim('cyl', 1, loc=(x,-0.0755,zc), rot=(math.pi/2,0,0), scale=(0.024,0.024,0.004), verts=32))
    rod = C.prim('cyl', 2, loc=(0,-0.058,zc-0.048), rot=(0,math.pi/2,0), scale=(0.008,0.008,0.56), verts=12)
    yb, zb, rb = 0.22, zc - 0.035, 0.058           # one continuous tube behind the marble plane (head joint -> foot joint). The camera looks down
    # and sits off to the side, so behind-plane parts shift with each key's tilt; a continuous tube (not separate stubs) keeps the flute unbroken.
    back = C.prim('cyl', 0, loc=(-0.08,yb,zb), rot=(0,math.pi/2,0), scale=(rb,rb,1.26), verts=40)
    crown = C.prim('sphere', 2, loc=(-0.715,yb,zb), scale=(0.035,0.062,0.062), verts=24)
    lip = C.prim('sphere', 0, loc=(-0.5,yb-0.03,zb+0.048), scale=(0.07,0.035,0.02), verts=32)
    C.cut(lip, C.prim('sphere', 1, loc=(-0.5,yb-0.035,zb+0.063), scale=(0.025,0.015,0.015), verts=20))
    joint = [C.prim('cyl', 2, loc=(x,yb,zb), rot=(0,math.pi/2,0), scale=(rb+0.006,rb+0.006,0.022), verts=40) for x in (-0.36,0.36)]
    fkeys = [C.prim('cyl', 2, loc=(x,yb-0.062,zb), rot=(math.pi/2,0,0), scale=(0.03,0.03,0.014), verts=24) for x in (0.42,0.5)]
    return [tube, rod, back, crown, lip] + joint + rings + cups + fkeys
