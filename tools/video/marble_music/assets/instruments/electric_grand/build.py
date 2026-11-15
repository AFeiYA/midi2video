"""electric_grand (jewelbox 02): key + pearl-white compact stage grand on a chrome X-stand."""
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
    P.append(C.prim('cube', 4, loc=(0,0.235,-0.035), scale=(0.66,0.12,0.06), bevel=0.01))           # black key bed
    P.append(C.prim('cube', 3, loc=(0,0.235,0.0), scale=(0.64,0.10,0.012), bevel=0.003))            # red felt
    P += stubs(C, variant, 4)
    P.append(C.shape_profile('eg_case', [(-0.48,-0.07),(0.18,-0.07),(0.44,-0.11),(0.44,-0.19),(-0.48,-0.19)], 0.08, 0.18, 1, bevel=0.015))
    P.append(C.shape_profile('eg_lid', [(-0.49,-0.062),(0.19,-0.062),(0.46,-0.10),(0.46,-0.085),(0.19,-0.048),(-0.49,-0.048)], 0.06, 0.20, 1, bevel=0.004))
    P.append(C.prim('cube', 3, loc=(-0.02,0.175,-0.13), scale=(0.84,0.01,0.025), bevel=0.003))      # red stripe
    P.append(C.prim('sphere', 2, loc=(-0.42,0.17,-0.165), scale=(0.016,0.012,0.016), verts=16))      # chrome knob
    # chrome X-stand
    for a, b in (((-0.34,-0.19,0.215), (0.26,-0.46)), ((0.26,-0.19,0.215), (-0.34,-0.46))):
        P.append(C.prim('cube', 2, loc=((a[0]+b[0])/2, 0.215, (a[1]+b[1])/2), rot=(0, __import__('math').atan2(b[0]-a[0], b[1]-a[1]), 0), scale=(0.035,0.04,0.66), bevel=0.01))
    P.append(C.prim('sphere', 4, loc=(-0.04,0.19,-0.325), scale=(0.03,0.03,0.03), verts=16))          # pivot knob
    for x in (-0.34, 0.26):
        P.append(C.prim('cube', 4, loc=(x,0.215,-0.465), scale=(0.14,0.06,0.025), bevel=0.008))      # rubber feet
    # coiled cable from the tail down to the floor
    for i in range(9):
        P.append(C.prim('torus', 4, loc=(0.47,0.21,-0.17-0.03*i), rot=(0.25,0,0), scale=(0.022,0.006), verts=16))
    return P
