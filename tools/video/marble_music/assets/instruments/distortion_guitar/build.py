"""distortion_guitar (jewelbox 20): chrome strings + red V guitar + mini amp stack."""
import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.

def key(C, variant, mi=0):
    if variant == 'black':
        return C.shape_profile('blackkey', [(-0.31,-0.07),(0.31,-0.07),(0.31,-0.0),(0.27,0.045),(-0.27,0.045),(-0.31,-0.0)], 0.22, -0.11, mi, bevel=0.01)
    return C.prim('cube', mi, loc=(0,0,0), scale=(0.62,0.30,0.09), bevel=0.012)
def stubs(C, variant, mi):
    return [] if variant == 'black' else [C.prim('cube', mi, loc=(x,0.225,0.03), scale=(0.11,0.13,0.07), bevel=0.012) for x in (-0.25, 0.25)]
def rod(C, a, b, r, mi, verts=16):
    """cylinder from (x,z,y) a to (x,z) b"""
    (x0, z0, y), (x1, z1) = a, b; L = math.hypot(x1-x0, z1-z0)
    return C.prim('cyl', mi, loc=((x0+x1)/2, y, (z0+z1)/2), rot=(0, math.atan2(x1-x0, z1-z0), 0), scale=(r, r, L), verts=verts)
def bar(C, a, b, w, d, mi, y, bevel=0.0):
    """flat bar (width w in XZ, depth d in Y) from (x,z) a to b at local y"""
    L = math.hypot(b[0]-a[0], b[1]-a[1])
    return C.prim('cube', mi, loc=((a[0]+b[0])/2, y, (a[1]+b[1])/2), rot=(0, -math.atan2(b[1]-a[1], b[0]-a[0]), 0), scale=(L, d, w), bevel=bevel)
def outline(inside, cx=0.0, cz=0.0, n=160, rmax=1.2, step=0.002):
    """star-shaped outline of a 2-D region (inside(x,z) -> bool) seen from (cx,cz) -> list of (x,z)"""
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n; ca, sa = math.cos(a), math.sin(a); r = 0.0
        while r < rmax and inside(cx+(r+step)*ca, cz+(r+step)*sa): r += step
        pts.append((cx+r*ca, cz+r*sa))
    return pts
def plate(C, name, inside, y0, depth, mi, cx=0.0, cz=0.0, bevel=0.012, n=160):
    return C.shape_profile(name, outline(inside, cx, cz, n), depth, y0, mi, bevel=bevel)
def violin_inside(L, ox=0.0):
    """violin-family body of length L (long axis = x, neck toward -x), centre at x=ox"""
    def f(x, z):
        x -= ox
        lo = ((x-0.22*L)/(0.26*L))**2 + (z/(0.29*L))**2 <= 1
        up = ((x+0.25*L)/(0.22*L))**2 + (z/(0.235*L))**2 <= 1
        wa = abs(x+0.02*L) < 0.14*L and abs(z) < 0.22*L
        cb = min(math.hypot(x+0.02*L, z-0.27*L), math.hypot(x+0.02*L, z+0.27*L)) < 0.12*L
        return (lo or up or wa) and not cb
    return f
def strings(C, ys, mis, r0, dr, x0=-0.31, x1=0.31):
    out = []
    for i, y in enumerate(ys):
        r = r0 - dr*i
        out.append(C.prim('cyl', mis[i] if isinstance(mis, (list, tuple)) else mis, loc=((x0+x1)/2,y,0.045-r), rot=(0,math.pi/2,0), scale=(r,r,x1-x0), verts=12))
    return out

VEE = [(-0.22, 0.06), (-0.22, -0.06), (0.42, -0.27), (0.49, -0.205), (0.13, 0.0), (0.49, 0.205), (0.42, 0.27)]
def build(C, variant=None):
    yb = 0.19
    P = [C.shape_profile('dg_body', VEE, 0.05, yb, 0, bevel=0.015)]
    P.append(C.shape_profile('dg_bind', VEE, 0.04, yb+0.005, 3, bevel=0.0)); P[-1].scale = (1.025, 1.0, 1.04)
    for x in (-0.12, -0.02):                                                                        # humbuckers
        P.append(C.prim('cube', 2, loc=(x,yb-0.012,0.0), scale=(0.06,0.012,0.16), bevel=0.008))
        for z in (-0.05,-0.017,0.017,0.05): P.append(C.prim('cyl', 1, loc=(x,yb-0.019,z), rot=(math.pi/2,0,0), scale=(0.008,0.008,0.004), verts=8))
    for x, z in ((0.25,-0.14),(0.33,-0.18),(0.25,0.14)):
        P.append(C.prim('cyl', 1, loc=(x,yb-0.012,z), rot=(math.pi/2,0,0), scale=(0.018,0.018,0.014), verts=16))
    P.append(C.prim('cube', 1, loc=(0.10,0.04,0.02), scale=(0.07,0.30,0.03), bevel=0.006))          # tune-o-matic bridge
    P.append(C.prim('cube', 3, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))
    P.append(C.prim('cube', 4, loc=(-0.47,yb-0.006,0.0), scale=(0.60,0.05,0.075), bevel=0.008))
    for x in (-0.33,-0.40,-0.47,-0.54,-0.61,-0.68): P.append(C.prim('cube', 1, loc=(x,yb-0.029,0.0), scale=(0.005,0.005,0.08)))
    P.append(C.shape_profile('dg_head', [(-0.76,-0.045),(-0.98,-0.07),(-0.92,0.0),(-0.98,0.07),(-0.76,0.045)], 0.05, yb, 2, bevel=0.008))
    for i in range(3):
        for s in (-1, 1): P.append(C.prim('cyl', 1, loc=(-0.80-0.05*i,yb,s*(0.065+0.008*i)), scale=(0.009,0.009,0.03), verts=10))
    # coiled cable from the lower wing to the amp
    for i in range(7): P.append(C.prim('torus', 2, loc=(0.44,yb-0.01,-0.27-0.028*i), rot=(0.3,0,0), scale=(0.02,0.006), verts=14))
    # mini amp stack
    P.append(C.prim('cube', 2, loc=(0.12,0.24,-0.42), scale=(0.46,0.09,0.20), bevel=0.015))
    P.append(C.prim('cube', 5, loc=(0.12,0.193,-0.44), scale=(0.40,0.006,0.13), bevel=0.003))
    P.append(C.prim('cube', 6, loc=(0.12,0.19,-0.44), scale=(0.37,0.006,0.11)))
    for i in range(6): P.append(C.prim('cyl', 1, loc=(-0.06+0.06*i,0.19,-0.345), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.01), verts=12))
    P += strings(C, (-0.095,-0.057,-0.019,0.019,0.057,0.095), 1, 0.012, 0.0012)
    return P
