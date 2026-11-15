"""orchestra_hit (jewelbox 32): timpani head striker + copper kettle + crash cymbal with impact rays."""
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

def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.02), scale=(0.60,0.30,0.05), bevel=0.01)]                     # calfskin head (top z=0.045)
    P.append(C.prim('cube', 1, loc=(0,0,-0.02), scale=(0.62,0.30,0.05), bevel=0.008))               # chrome counter-hoop
    k = C.prim('sphere', 2, loc=(0,0.215,-0.07), scale=(0.31,0.05,0.30), verts=64)                  # copper kettle (lower half)
    C.cut(k, C.prim('cube', 2, loc=(0,0.215,0.2), scale=(0.8,0.3,0.5)))
    P.append(k)
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.075), scale=(0.66,0.07,0.03), bevel=0.008))          # rim band
    for x in (-0.28,-0.18,-0.06,0.06,0.18,0.28):
        P.append(C.prim('cyl', 1, loc=(x,0.163,-0.17), scale=(0.005,0.005,0.18), verts=8))
        P.append(C.prim('cube', 1, loc=(x,0.165,-0.085), scale=(0.02,0.012,0.025), bevel=0.003))
    P.append(C.prim('torus', 1, loc=(0,0.22,-0.42), rot=(math.pi/2,0,0), scale=(0.22,0.012), verts=48))
    for x in (-0.20, 0.0, 0.20):
        P.append(rod(C, (x*0.6,-0.36,0.22), (x,-0.54), 0.012, 1))
        P.append(C.prim('sphere', 4, loc=(x,0.22,-0.555), scale=(0.022,0.022,0.022), verts=12))
    P.append(C.prim('cube', 4, loc=(0.08,0.19,-0.52), scale=(0.12,0.04,0.02), bevel=0.005))         # tuning pedal
    # crash cymbal on a stand (right) with impact rays
    cx, cz = 0.58, 0.10
    P.append(C.prim('cyl', 1, loc=(cx,0.26,(cz-0.56)/2), scale=(0.01,0.01,cz+0.56), verts=10))
    P.append(C.prim('cyl', 3, loc=(cx,0.22,cz), rot=(1.3,0,0.25), scale=(0.17,0.17,0.006), verts=48))
    P.append(C.prim('sphere', 3, loc=(cx,0.205,cz), scale=(0.04,0.015,0.035), verts=16))
    for i in range(9):
        a = i*2*math.pi/9 + 0.2; r0, r1 = 0.21, 0.27 + 0.03*(i % 2)
        P.append(bar(C, (cx+r0*math.cos(a), cz+r0*math.sin(a)), (cx+r1*math.cos(a), cz+r1*math.sin(a)), 0.012, 0.008, 3, 0.2))
    # crossed timpani mallets (left)
    for a_, b_ in (((-0.62,-0.40), (-0.38,0.02)), ((-0.38,-0.40), (-0.62,0.02))):
        P.append(rod(C, (a_[0],a_[1],0.19), b_, 0.007, 4, verts=8))
        P.append(C.prim('sphere', 5, loc=(b_[0],0.19,b_[1]), scale=(0.03,0.03,0.03), verts=16))
    return P
