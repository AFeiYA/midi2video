"""guitar: procedural striker. Acoustic-guitar top section: lacquered spruce soundboard with a sound hole and inlaid rosette, rosewood bridge with bone saddle, and six bronze/steel strings whose tops are flush with the contact face (the marble strikes the strings)."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    board = C.prim('cube', 0, loc=(0,0.055,-0.015), scale=(0.64,0.46,0.06), bevel=0.01)
    C.cut(board, C.prim('cyl', 3, loc=(0.16,0.12,0), scale=(0.075,0.075,0.2), verts=48))
    ros = C.prim('torus', 2, loc=(0.16,0.12,0.0155), scale=(0.09,0.007), verts=64)
    bridge = C.prim('cube', 2, loc=(-0.22,0,0.0225), scale=(0.06,0.26,0.015), bevel=0.004)
    saddle = C.prim('cube', 4, loc=(-0.225,0,0.033), scale=(0.008,0.22,0.006))
    strings = []
    for i, y in enumerate((-0.09,-0.054,-0.018,0.018,0.054,0.09)):
        r = 0.0095 - 0.0008*i
        strings.append(C.prim('cyl', 1, loc=(0.0,y,0.045-r), rot=(0,math.pi/2,0), scale=(r,r,0.62), verts=12))
    # camera-facing edge: dark rosewood binding + cream purfling line + side (ribs) so the guitar reads from the front
    ribs = C.prim('cube', 2, loc=(0,-0.165,-0.06), scale=(0.64,0.03,0.05), bevel=0.006)
    bind = C.prim('cube', 3, loc=(0,-0.1755,-0.012), scale=(0.645,0.012,0.012), bevel=0.003)
    purf = C.prim('cube', 4, loc=(0,-0.1785,-0.022), scale=(0.646,0.006,0.004))
    return [board, ros, bridge, saddle, ribs, bind, purf] + strings
