"""rhodes (jewelbox 03): key + black tolex suitcase electric piano on splayed chrome legs."""
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
    P.append(C.prim('cube', 2, loc=(0,0.235,-0.03), scale=(0.66,0.12,0.05), bevel=0.01))            # brushed silver name rail
    P.append(C.prim('cube', 3, loc=(-0.2,0.172,-0.03), scale=(0.12,0.01,0.03), bevel=0.003))        # red logo plate on the rail
    P += stubs(C, variant, 4)
    # suitcase: the top ~0.06 below the key hides behind it from the camera, so the silver lid band starts at z=-0.09
    P.append(C.prim('cube', 1, loc=(0,0.22,-0.215), scale=(0.98,0.12,0.19), bevel=0.04))            # black tolex suitcase (lower)
    P.append(C.prim('cube', 5, loc=(0,0.222,-0.10), scale=(0.98,0.12,0.09), bevel=0.03))            # silver 'sparkle top' lid
    P.append(C.prim('cube', 2, loc=(0,0.161,-0.145), scale=(0.94,0.006,0.012)))                      # silver lid seam
    P.append(C.prim('cube', 3, loc=(-0.28,0.162,-0.22), scale=(0.20,0.008,0.05), bevel=0.006))      # red logo plate on the case front
    for x in (0.12, 0.34):
        P.append(C.prim('cube', 2, loc=(x,0.166,-0.165), scale=(0.06,0.012,0.035), bevel=0.004))    # latches
    for x in (-0.46, 0.46):
        P.append(C.prim('sphere', 2, loc=(x,0.172,-0.30), scale=(0.02,0.012,0.02), verts=12))        # corner caps
    # splayed chrome legs (tapered: two cylinders) + pedal
    for x, dx in ((-0.36,-0.1), (0.36,0.1)):
        P.append(rod(C, (x,-0.31,0.20), (x+dx*0.6,-0.43), 0.022, 2))
        P.append(rod(C, (x+dx*0.6,-0.43,0.20), (x+dx,-0.55), 0.015, 2))
    P.append(C.prim('cube', 2, loc=(0.0,0.20,-0.53), scale=(0.12,0.06,0.025), bevel=0.008))         # sustain pedal
    P.append(rod(C, (0.06,-0.53,0.21), (0.3,-0.30), 0.006, 4, verts=8))                             # pedal cable
    return P
