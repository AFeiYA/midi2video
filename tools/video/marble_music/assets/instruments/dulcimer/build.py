"""dulcimer (jewelbox 12): string-topped walnut rail + trapezoid hammered dulcimer behind the marble plane."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,-0.005), scale=(0.62,0.30,0.08), bevel=0.01)]                  # walnut rail, top z=0.035
    for y in (-0.10,-0.05,0.0,0.05,0.10):                                                           # strings across the top: top z = 0.045
        P.append(C.prim('cyl', 3, loc=(0,y,0.039), rot=(0,math.pi/2,0), scale=(0.006,0.006,0.60), verts=10))
    for x in (-0.27, 0.27):                                                                         # end bridges under the strings
        P.append(C.prim('cube', 5, loc=(x,0,0.034), scale=(0.02,0.27,0.012)))
    # trapezoid dulcimer below (long side at the bottom)
    def hw(z): return 0.32 + 0.18*(-0.07 - z)/0.33
    P.append(C.shape_profile('dc_frame', [(-0.55,-0.43),(0.55,-0.43),(0.35,-0.045),(-0.35,-0.045)], 0.05, 0.215, 2, bevel=0.012))
    P.append(C.shape_profile('dc_board', [(-hw(-0.40),-0.40),(hw(-0.40),-0.40),(hw(-0.07),-0.07),(-hw(-0.07),-0.07)], 0.02, 0.20, 1))
    for k in range(12):
        z = -0.095 - 0.025*k; h = hw(z) - 0.02
        P.append(C.prim('cyl', 3, loc=(0,0.195,z), rot=(0,math.pi/2,0), scale=(0.0035,0.0035,2*h), verts=8))
    for x0, x1 in ((-0.14,-0.18), (0.18,0.24)):                                                    # bridges (perpendicular to the strings)
        P.append(C.prim('cube', 5, loc=((x0+x1)/2,0.19,-0.235), rot=(0,math.atan2(x1-x0,0.30),0), scale=(0.02,0.014,0.31), bevel=0.003))
    for x, z in ((-0.33,-0.25), (0.02,-0.24)):                                                      # gold rosettes
        P.append(C.prim('torus', 4, loc=(x,0.198,z), rot=(math.pi/2,0,0), scale=(0.045,0.008), verts=32))
        P.append(C.prim('cyl', 5, loc=(x,0.199,z), rot=(math.pi/2,0,0), scale=(0.038,0.038,0.003), verts=24))
    # crossed hammers (thin canes with flat heads) lying in front
    for a, b in (((-0.42,-0.52), (0.10,-0.30)), ((0.42,-0.52), (-0.10,-0.30))):
        L = math.hypot(b[0]-a[0], b[1]-a[1])
        P.append(C.prim('cyl', 2, loc=((a[0]+b[0])/2,0.17,(a[1]+b[1])/2), rot=(0,math.atan2(b[0]-a[0],b[1]-a[1]),0), scale=(0.006,0.006,L), verts=8))
        P.append(C.prim('cube', 2, loc=(b[0],0.168,b[1]), rot=(0,math.atan2(b[0]-a[0],b[1]-a[1]),0), scale=(0.05,0.022,0.018), bevel=0.006))
    return P
