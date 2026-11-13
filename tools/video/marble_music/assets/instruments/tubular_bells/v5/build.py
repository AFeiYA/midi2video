"""tubular bells v5: polished brass hanging rail (struck); five graded brass chime tubes with crown caps hang straight down behind it (world-vertical, meta.hanging)."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
def build(C, variant=None):
    rail = C.prim('cube', 0, loc=(0,0,0.025), scale=(0.62,0.12,0.04), bevel=0.01)
    hooks = [C.prim('cube', 3, loc=(x,0.13,0.02), scale=(0.02,0.16,0.02)) for x in (-0.24,-0.12,0.0,0.12,0.24)]
    ends = [C.prim('sphere', 0, loc=(x,0,0.025), scale=(0.02,0.065,0.02), verts=24) for x in (-0.29,0.29)]
    return [rail] + hooks + ends
