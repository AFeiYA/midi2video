"""marimba v4 (resonator is a world-vertical hanging part, see meta.hanging):: procedural striker. Honduras-rosewood marimba bar with the traditional carved arch underneath, suspension cords at the nodes and a dark-bronze resonator tube behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    pts = [(-0.31,0.045),(0.31,0.045),(0.31,-0.045)]
    n = 14
    for i in range(n+1):
        x = 0.22 - 0.44*i/n; pts.append((x, -0.045 + 0.038*(1-(x/0.22)**2)))
    pts.append((-0.31,-0.045))
    bar = C.shape_profile('marimba_bar', pts, 0.32, -0.16, 0, bevel=0.012)
    cords = [C.prim('cyl', 1, loc=(x,0.06,-0.015), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.46), verts=12) for x in (-0.14,0.14)]
    return [bar] + cords
