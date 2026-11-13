"""kalimba: procedural striker. Kalimba section: a spring-steel tine (struck, top flush with contact face) flanked by two shorter tines, resting on a steel bridge rod over a lacquered walnut soundboard with a sound hole behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    tine = C.prim('cube', 0, loc=(0,0,0.031), scale=(0.62,0.075,0.028), bevel=0.008)
    side = [C.prim('cube', 1, loc=(-0.035,y,0.024), scale=(0.55,0.06,0.024), bevel=0.007) for y in (-0.105,0.105)]
    bridge = C.prim('cyl', 1, loc=(-0.2,0,0.0085), rot=(math.pi/2,0,0), scale=(0.0085,0.0085,0.30), verts=16)
    board = C.prim('cube', 2, loc=(0,0.055,-0.0225), scale=(0.64,0.46,0.045), bevel=0.012)
    C.cut(board, C.prim('cyl', 3, loc=(0.16,0.2,0), scale=(0.045,0.045,0.2), verts=32))
    return [tine, bridge, board] + side
