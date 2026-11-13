"""guitar v4: sunburst spruce top, sound hole + wide dark rosette moved towards the camera, thick black-coated strings (contrast on amber) over a short neck stub with frets."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant=None):
    board = C.prim('cube', 0, loc=(0,0.055,-0.015), scale=(0.64,0.46,0.06), bevel=0.01)
    hx, hy = 0.12, -0.02
    C.cut(board, C.prim('cyl', 3, loc=(hx,hy,0), scale=(0.07,0.07,0.2), verts=48))
    ros_out = C.prim('cyl', 3, loc=(hx,hy,0.0152), scale=(0.115,0.115,0.0012), verts=64)    # dark rosette band (flush)
    ros_in  = C.prim('torus', 4, loc=(hx,hy,0.0158), scale=(0.093,0.0035), verts=64)        # cream inlay line inside the band
    C.cut(ros_out, C.prim('cyl', 3, loc=(hx,hy,0.0152), scale=(0.07,0.07,0.01), verts=48))
    bridge = C.prim('cube', 2, loc=(-0.2,0,0.0225), scale=(0.07,0.30,0.015), bevel=0.004)
    saddle = C.prim('cube', 4, loc=(-0.205,0,0.033), scale=(0.008,0.24,0.006))
    neck = C.prim('cube', 2, loc=(0.265,0,0.022), scale=(0.09,0.24,0.016), bevel=0.004)       # fingerboard stub (inside x<=0.31)
    frets = [C.prim('cube', 5, loc=(x,0,0.0305), scale=(0.004,0.235,0.003)) for x in (0.235,0.275)]
    strings = []
    for i, y in enumerate((-0.095,-0.057,-0.019,0.019,0.057,0.095)):
        r = 0.0135 - 0.0009*i
        strings.append(C.prim('cyl', 1, loc=(0.0,y,0.045-r), rot=(0,math.pi/2,0), scale=(r,r,0.62), verts=12))
    ribs = C.prim('cube', 2, loc=(0,-0.165,-0.06), scale=(0.64,0.03,0.05), bevel=0.006)
    bind = C.prim('cube', 4, loc=(0,-0.1765,-0.012), scale=(0.645,0.014,0.016), bevel=0.003)
    return [board, ros_out, ros_in, bridge, saddle, neck, ribs, bind] + frets + strings
