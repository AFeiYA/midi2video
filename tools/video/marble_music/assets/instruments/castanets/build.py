"""castanets: procedural striker. Pair of lacquered dark-rosewood castanet shells (two half-ellipsoids with a dark seam), hung from the wall pegs by a red cord loop; the marble strikes the crown of the upper shell."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    up = C.prim('sphere', 0, loc=(0,0,-0.012), scale=(0.29,0.17,0.057), verts=48)
    C.cut(up, C.prim('cube', 1, loc=(0,0,-0.012-0.1), scale=(0.8,0.5,0.2), smooth=False))
    lo = C.prim('sphere', 0, loc=(0,0,-0.018), scale=(0.29,0.17,0.057), verts=48)
    C.cut(lo, C.prim('cube', 1, loc=(0,0,-0.018+0.1), scale=(0.8,0.5,0.2), smooth=False))
    seam = C.prim('cyl', 1, loc=(0,0,-0.015), scale=(0.27,0.155,0.004), verts=48)
    ear = C.prim('cube', 0, loc=(-0.285,0,-0.015), scale=(0.05,0.07,0.05), bevel=0.012)
    cord = C.prim('torus', 2, loc=(-0.3,0.12,-0.015), rot=(0,math.pi/2,0), scale=(0.06,0.008), verts=24)
    return [up, lo, seam, ear, cord]
