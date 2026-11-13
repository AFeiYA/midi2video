"""piano v5: realistic ivory/ebony keys chosen per note from its pitch class (shape follows the note: naturals white-key shape, sharps black-key shape) plus two small ebony black-key stubs on the key bed behind the marble plane so a C-major melody still reads as a keyboard. v3 text: Real piano keys alternating ivory white keys (flat-topped, bevelled) and glossy ebony black keys (taller, tapered ends), sitting on a black key-bed rail with a red felt strip behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall at y=0.30)
def build(C, variant='white'):
    parts = []
    if variant == 'black':
        parts.append(C.shape_profile('blackkey', [(-0.31,-0.07),(0.31,-0.07),(0.31,-0.0),(0.27,0.045),(-0.27,0.045),(-0.31,-0.0)], 0.22, -0.11, 0, bevel=0.01))
    else:
        parts.append(C.prim('cube', 0, loc=(0,0,0), scale=(0.62,0.32,0.09), bevel=0.012))
    parts.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.66,0.12,0.06), bevel=0.008))
    parts.append(C.prim('cube', 2, loc=(0,0.235,-0.0), scale=(0.64,0.10,0.012), bevel=0.003))
    if variant != 'black':
        for x in (-0.25, 0.25):                                                       # neighbouring black keys, behind the marble plane
            parts.append(C.prim('cube', 1, loc=(x,0.225,0.03), scale=(0.11,0.13,0.07), bevel=0.012))
    return parts
