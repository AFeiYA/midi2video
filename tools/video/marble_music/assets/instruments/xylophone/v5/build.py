"""xylophone: procedural striker. Gloss-painted rainbow xylophone bar (colour cycles bar to bar), resting on two red felt strips over a pale birch frame rail behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    bar = C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.018)
    felts = [C.prim('cube', 1, loc=(x,0.07,-0.06), scale=(0.05,0.44,0.03), bevel=0.004) for x in (-0.15,0.15)]
    frame = C.prim('cube', 2, loc=(0,0.225,-0.09), scale=(0.66,0.15,0.06), bevel=0.01)
    return [bar, frame] + felts
