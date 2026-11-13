"""glockenspiel: procedural striker. Thin polished-steel glockenspiel bar on two dark walnut frame rails, fixed by two small domed screws with red felt washers."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    bar = C.prim('cube', 0, loc=(0,0,0.0225), scale=(0.62,0.26,0.045), bevel=0.008)
    rails = [C.prim('cube', 1, loc=(x,0.065,-0.0225), scale=(0.06,0.46,0.045), bevel=0.008) for x in (-0.2,0.2)]
    screws, felts = [], []
    for x in (-0.2,0.2):
        felts.append(C.prim('cyl', 3, loc=(x,0,0.0465), scale=(0.022,0.022,0.003), verts=24))
        screws.append(C.prim('sphere', 2, loc=(x,0,0.046), scale=(0.015,0.015,0.006), verts=20))
    return [bar] + rails + screws + felts
