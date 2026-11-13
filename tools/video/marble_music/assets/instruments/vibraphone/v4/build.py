"""vibraphone v4 (resonator is a world-vertical hanging part, see meta.hanging):: procedural striker. Brushed-aluminium vibraphone bar with rounded edges, two maroon suspension cords through the nodal points, and a gold anodised resonator tube hanging behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    bar = C.prim('cube', 0, scale=(0.62,0.32,0.09), bevel=0.016)
    cords = [C.prim('cyl', 1, loc=(x,0.06,0), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.46), verts=12) for x in (-0.14,0.14)]
    return [bar] + cords
