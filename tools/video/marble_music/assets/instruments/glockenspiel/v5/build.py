"""glockenspiel v5: struck steel bar on top of a red lacquered trapezoid case holding four more graded steel bars with brass screws - case and lower bars behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
def build(C, variant=None):
    bar = C.prim('cube', 0, loc=(0,0,0.0), scale=(0.62,0.30,0.09), bevel=0.01)
    parts = [bar]
    for x in (-0.2,0.2):
        parts.append(C.prim('cyl', 3, loc=(x,0,0.0465), scale=(0.024,0.024,0.003), verts=24))
        parts.append(C.prim('sphere', 2, loc=(x,0,0.046), scale=(0.016,0.016,0.006), verts=20))
    case = C.shape_profile('glock_case', [(-0.34,0.06),(0.34,0.06),(0.24,-0.44),(-0.24,-0.44)], 0.08, 0.2, 1, bevel=0.02)
    parts.append(case)
    for i, L in enumerate((0.52,0.46,0.40,0.34)):
        z = -0.1 - 0.088*i
        parts.append(C.prim('cube', 4, loc=(0,0.178,z), scale=(L,0.04,0.065), bevel=0.008))
        for x in (-L/2+0.05, L/2-0.05): parts.append(C.prim('sphere', 2, loc=(x,0.155,z), scale=(0.012,0.008,0.012), verts=16))
    return parts
