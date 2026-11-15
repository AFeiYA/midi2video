"""grand_piano (jewelbox 01): pitch-chosen ivory/ebony key + black lacquer grand piano profile behind the marble plane."""
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
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.66,0.12,0.06), bevel=0.008))          # key bed (lacquer)
    P.append(C.prim('cube', 3, loc=(0,0.235,0.0), scale=(0.64,0.10,0.012), bevel=0.003))            # red felt
    P += stubs(C, variant, 1)
    # case (side elevation): straight spine on the left, rounded tail on the right
    P.append(C.shape_profile('gp_case', [(-0.58,-0.07),(0.46,-0.07),(0.57,-0.10),(0.61,-0.15),(0.58,-0.21),(0.48,-0.24),(-0.58,-0.24)], 0.07, 0.19, 1, bevel=0.012))
    P.append(C.prim('cube', 2, loc=(0.0,0.185,-0.075), scale=(1.14,0.012,0.012), bevel=0.003))     # gold rims
    P.append(C.prim('cube', 2, loc=(-0.05,0.185,-0.235), scale=(1.04,0.012,0.01), bevel=0.003))
    # lid propped open (hinged near the keys, rising to the tail), gold prop stick, gold strings under it
    P.append(C.prim('cube', 1, loc=(0.307,0.262,0.098), rot=(0,-0.5,0), scale=(0.70,0.04,0.02), bevel=0.006))
    P.append(C.prim('cube', 2, loc=(0.307,0.24,0.093), rot=(0,-0.5,0), scale=(0.66,0.004,0.008)))
    P.append(rod(C, (0.50,-0.07,0.235), (0.50,0.19), 0.009, 2))
    for i in range(6):
        P.append(rod(C, (0.05,-0.062,0.205+0.012*i), (0.58,-0.062-0.012*i), 0.0035, 2, verts=8))
    # legs with brass casters, lyre + pedals
    for x in (-0.50, 0.46):
        P.append(C.prim('cyl', 1, loc=(x,0.215,-0.37), scale=(0.038,0.038,0.24), verts=20))
        P.append(C.prim('cyl', 1, loc=(x,0.215,-0.265), scale=(0.055,0.055,0.04), verts=20))
        P.append(C.prim('sphere', 2, loc=(x,0.215,-0.505), scale=(0.038,0.038,0.03), verts=16))
    for x in (-0.03, 0.03):
        P.append(rod(C, (x,-0.24,0.215), (x*1.6,-0.43), 0.008, 2))
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.445), scale=(0.16,0.05,0.035), bevel=0.008))
    for x in (-0.04, 0.0, 0.04):
        P.append(C.prim('cube', 2, loc=(x,0.18,-0.455), scale=(0.018,0.05,0.008), bevel=0.002))
    return P
