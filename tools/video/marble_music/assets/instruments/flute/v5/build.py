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
    # v5b: the foot joint continues the body IN the marble slab (keep-out clean up to x=0.44); the head joint cannot (the marble
    # arrives from that side), so it is an 'aligned' part (meta.aligned, built by build_aligned) placed behind the marble plane on the
    # camera ray through the body axis - it continues the tube exactly in the image instead of reading as a second, offset tube.
    foot = C.prim('cyl', 0, loc=(0.37,0,zc), rot=(0,math.pi/2,0), scale=(r*0.94,r*0.94,0.13), verts=48)
    fcap = C.prim('cyl', 2, loc=(0.433,0,zc), rot=(0,math.pi/2,0), scale=(r*0.98,r*0.98,0.012), verts=48)
    joint = [C.prim('cyl', 2, loc=(0.322,0,zc), rot=(0,math.pi/2,0), scale=(0.071,0.071,0.02), verts=48)]
    fkeys = [C.prim('cyl', 2, loc=(x,-0.066,zc), rot=(math.pi/2,0,0), scale=(0.028,0.028,0.012), verts=24) for x in (0.36,0.41)]
    return [tube, rod, foot, fcap] + joint + rings + cups + fkeys

def build_aligned(C, name):
    """head joint for meta.aligned['head']: modelled along -X from the origin (length 0.40), axis at y=z=0; scene.py places it per key."""
    r = 0.065*0.94
    head = C.prim('cyl', 0, loc=(-0.2,0,0), rot=(0,math.pi/2,0), scale=(r,r,0.40), verts=48)
    ring = C.prim('cyl', 2, loc=(-0.015,0,0), rot=(0,math.pi/2,0), scale=(0.071,0.071,0.02), verts=48)
    crown = C.prim('sphere', 2, loc=(-0.40,0,0), scale=(0.028,0.063,0.063), verts=24)
    lip = C.prim('sphere', 0, loc=(-0.2,-0.045,0.045), scale=(0.06,0.03,0.016), verts=32)
    hole = C.prim('sphere', 1, loc=(-0.2,-0.05,0.058), scale=(0.022,0.012,0.012), verts=20)
    return [head, ring, crown, lip, hole]
