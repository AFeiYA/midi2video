"""koto (hook50 06): rosewood edge rail (struck) + face-on paulownia board, 13 strings, diagonal ivory bridges, rosewood end caps."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.0), scale=(0.62,0.16,0.09), bevel=0.012)]
    for x in (-0.2,0.0,0.2): P.append(C.prim('cube', 4, loc=(x,-0.0805,0.0), scale=(0.006,0.002,0.07)))   # gold inlay ticks on the front face
    # board (slightly bowed top edge), behind the marble plane
    pts = [(-0.46,-0.30)]
    for i in range(13): x = -0.46 + 0.92*i/12; pts.append((x, -0.035 + 0.02*(1-(x/0.46)**2)))
    pts.append((0.46,-0.30))
    P.append(C.shape_profile('koto_board', pts, 0.07, 0.19, 1, bevel=0.015))
    for x in (-0.47,0.47): P.append(C.prim('cube', 0, loc=(x,0.215,-0.165), scale=(0.07,0.07,0.29), bevel=0.012))  # rosewood end caps
    for x in (-0.43,0.43): P.append(C.prim('cube', 4, loc=(x,0.178,-0.165), scale=(0.008,0.004,0.27)))            # gold trim
    for i in range(13):
        z = -0.06 - 0.017*i
        if i % 2 == 0: P.append(C.prim('cyl', 2, loc=(0,0.183,z), rot=(0,math.pi/2,0), scale=(0.0012,0.0012,0.84), verts=6))
        bx = 0.25 - 0.4*i/12
        P.append(C.shape_profile(f'ji{i}', [(bx-0.02,z-0.007),(bx+0.02,z-0.007),(bx+0.005,z+0.007),(bx-0.005,z+0.007)], 0.016, 0.168, 3))
    return P
