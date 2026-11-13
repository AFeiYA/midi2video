"""steel_drums: procedural striker. Mini chrome steel pan seen from above: raised rim, sunken dish, the struck note as a hammered dome in the centre (flush with contact face), four smaller note domes around it, and a short skirt."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    pan = C.prim('cyl', 1, loc=(0,0,-0.0475), scale=(0.29,0.29,0.155), bevel=0.012, verts=64)
    C.cut(pan, C.prim('cyl', 1, loc=(0,0,0.05), scale=(0.262,0.262,0.09), verts=64))
    note = C.prim('sphere', 0, loc=(0,0,0.005), scale=(0.13,0.11,0.04), verts=48)
    domes = [C.prim('sphere', 1, loc=(0.19*math.cos(t),0.17*math.sin(t),0.005), scale=(0.055,0.05,0.02), verts=32) for t in (0.6,2.55,3.75,5.6)]
    ring = C.prim('torus', 2, loc=(0,0,0.006), scale=(0.135,0.004), verts=64)
    return [pan, note, ring] + domes
