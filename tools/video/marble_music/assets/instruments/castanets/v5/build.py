"""castanets v5: an open clam pair seen face-on - front shell (struck, crown flush with contact face) and a second shell behind it, dark rims, ears with a red cord loop."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
def build(C, variant=None):
    a = C.prim('sphere', 0, loc=(0,0,-0.125), scale=(0.17,0.07,0.17), verts=48)                 # front shell, top at z=0.045
    rimA = C.prim('torus', 1, loc=(0,-0.005,-0.125), rot=(math.pi/2,0,0), scale=(0.158,0.009), verts=64)
    b = C.prim('sphere', 0, loc=(0.13,0.205,-0.15), scale=(0.17,0.045,0.17), verts=48)          # back shell (behind marble plane)
    rimB = C.prim('torus', 1, loc=(0.13,0.16,-0.15), rot=(math.pi/2,0,0), scale=(0.165,0.008), verts=64)
    earA = C.prim('sphere', 0, loc=(-0.15,0.0,0.0), scale=(0.05,0.05,0.04), verts=24)
    earB = C.prim('sphere', 0, loc=(-0.03,0.2,-0.005), scale=(0.05,0.04,0.04), verts=24)
    cord = C.prim('torus', 2, loc=(-0.11,0.12,0.03), rot=(0,0,math.pi/2.6), scale=(0.11,0.009), verts=48)
    return [a, rimA, b, rimB, earA, earB, cord]
