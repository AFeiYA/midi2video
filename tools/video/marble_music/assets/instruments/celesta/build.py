"""celesta (jewelbox 05): key + honey-wood upright cabinet with arched top and a gilt fretwork panel."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def key(C, variant, mi=0):
    if variant == 'black':
        return C.shape_profile('blackkey', [(-0.31,-0.07),(0.31,-0.07),(0.31,-0.0),(0.27,0.045),(-0.27,0.045),(-0.31,-0.0)], 0.22, -0.11, mi, bevel=0.01)
    return C.prim('cube', mi, loc=(0,0,0), scale=(0.62,0.30,0.09), bevel=0.012)
def stubs(C, variant, mi):
    """two black-key stubs on the key bed behind the marble plane (natural keys only) so a C-major melody still reads as a keyboard"""
    return [] if variant == 'black' else [C.prim('cube', mi, loc=(x,0.225,0.03), scale=(0.11,0.13,0.07), bevel=0.012) for x in (-0.25, 0.25)]
def rod(C, a, b, r, mi, verts=16):
    """cylinder from (x,z) a to b at local y = a[2]"""
    import math
    (x0, z0, y), (x1, z1) = a, b; L = math.hypot(x1-x0, z1-z0)
    return C.prim('cyl', mi, loc=((x0+x1)/2, y, (z0+z1)/2), rot=(0, math.atan2(x1-x0, z1-z0), 0), scale=(r, r, L), verts=verts)

def build(C, variant='white'):
    import math
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.03), scale=(0.70,0.10,0.06), bevel=0.01))            # key slip
    P += stubs(C, variant, 3)
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.25), scale=(0.74,0.09,0.36), bevel=0.02))            # lower cabinet
    P.append(C.prim('cube', 2, loc=(0,0.188,-0.25), scale=(0.62,0.004,0.26), bevel=0.002))          # gold panel frame
    P.append(C.prim('cube', 1, loc=(0,0.185,-0.25), scale=(0.58,0.004,0.22), bevel=0.002))
    P.append(C.prim('cube', 1, loc=(0,0.255,0.14), scale=(0.74,0.06,0.34), bevel=0.02))             # upper cabinet behind the key
    P.append(C.prim('cyl', 1, loc=(0,0.255,0.31), rot=(math.pi/2,0,0), scale=(0.37,0.12,0.06), verts=48))   # arched top
    P.append(C.prim('sphere', 2, loc=(0,0.23,0.43), scale=(0.035,0.02,0.035), verts=16))            # crest finial
    P.append(C.prim('cube', 3, loc=(0,0.222,0.17), scale=(0.56,0.004,0.13), bevel=0.002))          # fretwork panel: dark backing
    P.append(C.prim('cube', 2, loc=(0,0.22,0.17), scale=(0.58,0.006,0.15), bevel=0.004))            # gilt frame (outer)
    P.append(C.prim('cube', 3, loc=(0,0.217,0.17), scale=(0.54,0.006,0.11)))
    for k in range(11):                                                                             # gilt slats with a lozenge in the middle
        x = -0.25 + 0.05*k; P.append(C.prim('cube', 2, loc=(x,0.215,0.17), scale=(0.012,0.006,0.11)))
    P.append(C.prim('cube', 2, loc=(0,0.213,0.17), rot=(0,math.pi/4,0), scale=(0.07,0.006,0.07)))
    # gilt lyre with pedal, ball-foot legs
    for x in (-0.05, 0.05):
        P.append(rod(C, (x,-0.43,0.215), (x*1.8,-0.55), 0.009, 2))
    P.append(C.prim('cube', 2, loc=(0,0.19,-0.555), scale=(0.08,0.06,0.012), bevel=0.003))
    for x in (-0.33, 0.33):
        P.append(C.prim('cyl', 1, loc=(x,0.23,-0.48), scale=(0.03,0.03,0.12), verts=16))
        P.append(C.prim('sphere', 2, loc=(x,0.23,-0.55), scale=(0.035,0.035,0.03), verts=16))
    return P
