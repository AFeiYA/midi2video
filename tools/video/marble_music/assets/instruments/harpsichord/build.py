"""harpsichord (jewelbox 04): reversed keys + upper manual + red lacquer case with painted lid and turned gilt legs."""
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
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.66,0.12,0.06), bevel=0.008))          # key bed (red lacquer)
    # upper manual: one octave of tiny reversed keys (naturals ebony, sharps bone) behind the striker
    nat = [-0.27 + 0.09*i for i in range(7)]
    for x in nat: P.append(C.prim('cube', 4, loc=(x,0.235,0.04), scale=(0.082,0.10,0.03), bevel=0.004))
    for x in (nat[0]+0.045, nat[1]+0.045, nat[3]+0.045, nat[4]+0.045, nat[5]+0.045):
        P.append(C.prim('cube', 3, loc=(x,0.215,0.065), scale=(0.045,0.06,0.03), bevel=0.004))
    P.append(C.prim('cube', 1, loc=(0,0.27,0.07), scale=(0.66,0.04,0.09), bevel=0.008))             # name board behind the upper manual
    P.append(C.prim('cube', 2, loc=(0,0.248,0.11), scale=(0.66,0.01,0.01)))
    # long wing case with angled bentside, gold trim
    P.append(C.shape_profile('hc_case', [(-0.52,-0.07),(0.58,-0.07),(0.58,-0.11),(0.30,-0.17),(-0.52,-0.17)], 0.07, 0.19, 1, bevel=0.01))
    P.append(C.prim('cube', 2, loc=(0.03,0.185,-0.072), scale=(1.10,0.012,0.012)))
    P.append(C.prim('cube', 2, loc=(-0.11,0.185,-0.168), scale=(0.82,0.012,0.012)))
    # open lid: lacquer outside, painted panel inside facing the camera, gold border
    import math
    lid = dict(loc=(0.30,0.265,0.03), rot=(0,-0.36,0))
    P.append(C.prim('cube', 1, scale=(0.60,0.03,0.30), bevel=0.01, **lid))
    P.append(C.prim('cube', 2, loc=(0.30,0.248,0.03), rot=(0,-0.36,0), scale=(0.56,0.006,0.26)))
    P.append(C.prim('cube', 5, loc=(0.30,0.244,0.03), rot=(0,-0.36,0), scale=(0.52,0.006,0.22)))
    # gilt turned legs: column + rings + ball feet
    for x in (-0.44, 0.0, 0.44):
        P.append(C.prim('cyl', 2, loc=(x,0.215,-0.31), scale=(0.018,0.018,0.26), verts=16))
        for z in (-0.20, -0.30, -0.40): P.append(C.prim('sphere', 2, loc=(x,0.215,z), scale=(0.032,0.032,0.026), verts=16))
        P.append(C.prim('sphere', 2, loc=(x,0.215,-0.45), scale=(0.03,0.03,0.022), verts=16))
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.36), scale=(0.90,0.025,0.02), bevel=0.004))          # stretcher
    return P
