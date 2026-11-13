"""glockenspiel v4: full-thickness polished steel bar, red-lacquered frame rails, brass screws on red felt washers."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    bar = C.prim('cube', 0, loc=(0,0,0.0), scale=(0.62,0.30,0.09), bevel=0.01)
    rails = [C.prim('cube', 1, loc=(x,0.0375,-0.065), scale=(0.07,0.515,0.04), bevel=0.008) for x in (-0.2,0.2)]   # reach out in front of the bar (y to -0.22) so they read
    screws, felts = [], []
    for x in (-0.2,0.2):
        felts.append(C.prim('cyl', 3, loc=(x,0,0.0465), scale=(0.024,0.024,0.003), verts=24))
        screws.append(C.prim('sphere', 2, loc=(x,0,0.046), scale=(0.016,0.016,0.006), verts=20))
    return [bar] + rails + screws + felts
