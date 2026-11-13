"""kalimba v5: steel bridge bar (struck) over a fan of nine tines of uneven (V-shaped) lengths on a rounded walnut board with a sound hole - all behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
def build(C, variant=None):
    bar = C.prim('cube', 0, loc=(0,0,0.03), scale=(0.62,0.12,0.03), bevel=0.008)                # bridge bar, top z=0.045
    legs = [C.prim('cube', 1, loc=(x,0.12,0.03), scale=(0.04,0.13,0.026), bevel=0.004) for x in (-0.27,0.27)]
    tines = []
    n = 9
    for i in range(n):
        x = -0.26 + 0.52*i/(n-1); L = 0.38 - 0.24*abs(i-(n-1)/2)/((n-1)/2)
        tines.append(C.prim('cube', 1, loc=(x,0.172,0.02-L/2), scale=(0.036,0.016,L), bevel=0.006))
    board = C.prim('cube', 2, loc=(0,0.232,-0.2), scale=(0.68,0.09,0.56), bevel=0.06)
    C.cut(board, C.prim('cyl', 3, loc=(0,0.18,-0.4), rot=(math.pi/2,0,0), scale=(0.06,0.06,0.2), verts=40))
    return [bar, board] + legs + tines
