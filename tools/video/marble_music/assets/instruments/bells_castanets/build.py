"""bells_castanets (hook50 01): brass chime rail with black end knobs; castanet pair (front + back shell, red cord) hangs off the right end, behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def build(C, variant=None):
    rail = C.prim('cube', 0, loc=(0,0,0.0), scale=(0.62,0.12,0.09), bevel=0.014)
    ends = [C.prim('sphere', 2, loc=(x,0.0,0.0), scale=(0.03,0.06,0.044), verts=24) for x in (-0.29,0.29)]
    beam = C.prim('cube', 2, loc=(0,0.215,0.0), scale=(0.66,0.05,0.035), bevel=0.008)      # dark hanger beam behind the rail
    hooks = [C.prim('cyl', 3, loc=(x,0.215,0.0), scale=(0.012,0.012,0.05), verts=12) for x in (-0.25,-0.15,-0.05,0.05,0.15,0.25)]
    # castanet pair hanging off the right end of the beam
    cx, cz = 0.47, -0.21
    cord = C.prim('cyl', 5, loc=(0.40,0.2,-0.06), rot=(0,-0.5,0), scale=(0.009,0.009,0.15), verts=10)
    shA = C.prim('sphere', 4, loc=(cx,0.195,cz), scale=(0.13,0.032,0.14), verts=48)
    rimA = C.prim('torus', 2, loc=(cx,0.168,cz), rot=(math.pi/2,0,0), scale=(0.125,0.008), verts=56)
    shB = C.prim('sphere', 4, loc=(cx+0.08,0.25,cz-0.04), scale=(0.13,0.03,0.14), verts=48)
    knot = C.prim('sphere', 5, loc=(cx-0.04,0.17,cz+0.13), scale=(0.03,0.02,0.03), verts=16)
    return [rail, beam, cord, shA, rimA, shB, knot] + ends + hooks
