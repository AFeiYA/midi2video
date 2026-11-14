"""music_box (hook50 02): brass comb (struck) + pinned cylinder + walnut box with open red-velvet lid and winding key."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def build(C, variant=None):
    P = []
    P.append(C.prim('cube', 0, loc=(0,0,0.0275), scale=(0.62,0.20,0.035), bevel=0.006))         # comb base strip (contact top z=0.045)
    n = 17
    for i in range(n):                                                                            # tines, graded (long bass -> short treble)
        x = -0.28 + 0.56*i/(n-1); L = 0.06 - 0.025*i/(n-1)
        P.append(C.prim('cube', 0, loc=(x,0.0,0.01-L/2), scale=(0.022,0.16,L), bevel=0.003))
    # behind the marble plane: pinned cylinder
    cyl = C.prim('cyl', 3, loc=(0,0.2,-0.115), rot=(0,math.pi/2,0), scale=(0.055,0.055,0.52), verts=40); P.append(cyl)
    for i in range(26):
        x = -0.24 + 0.48*((i*7)%26)/25; a = (i*2.39)%(math.pi)-math.pi/2
        P.append(C.prim('sphere', 3, loc=(x,0.2-0.055*math.cos(a)*0.9,-0.115+0.055*math.sin(a)), scale=(0.008,0.008,0.008), verts=8, smooth=False))
    for x in (-0.275,0.275): P.append(C.prim('cyl', 4, loc=(x,0.2,-0.115), rot=(0,math.pi/2,0), scale=(0.07,0.07,0.02), verts=32))
    # walnut box (front face toward the camera)
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.29), scale=(0.70,0.12,0.24), bevel=0.02))
    P.append(C.prim('cube', 3, loc=(0,0.153,-0.29), scale=(0.62,0.004,0.17), bevel=0.003))       # brass inlay frame
    P.append(C.prim('cube', 1, loc=(0,0.150,-0.29), scale=(0.58,0.004,0.14), bevel=0.003))       # inner panel
    P.append(C.prim('cyl', 4, loc=(0,0.146,-0.27), rot=(math.pi/2,0,0), scale=(0.018,0.018,0.006), verts=20))   # keyhole
    P.append(C.prim('cube', 4, loc=(0,0.146,-0.295), scale=(0.012,0.006,0.03)))
    # open lid behind: red velvet inside face toward camera, walnut rim
    P.append(C.shape_profile('mb_lid', [(-0.35,-0.16),(0.35,-0.16),(0.35,0.20),(-0.35,0.20)], 0.02, 0.265, 1, bevel=0.01))
    P.append(C.shape_profile('mb_velvet', [(-0.32,-0.14),(0.32,-0.14),(0.32,0.17),(-0.32,0.17)], 0.004, 0.261, 2))
    # winding key on the right side
    P.append(C.prim('cyl', 3, loc=(0.385,0.215,-0.27), rot=(0,math.pi/2,0), scale=(0.012,0.012,0.07), verts=12))
    P.append(C.prim('torus', 3, loc=(0.45,0.215,-0.24), rot=(math.pi/2,0,0), scale=(0.04,0.01), verts=24))
    P.append(C.prim('torus', 3, loc=(0.45,0.215,-0.30), rot=(math.pi/2,0,0), scale=(0.04,0.01), verts=24))
    return P
