"""fretless_bass (jewelbox 22): 4 strings + violet offset-waist bass, tortoise guard, lined fretless ebony board."""
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

JAZZ = [(0.4, 0.0), (0.39, 0.14), (0.32, 0.23), (0.2, 0.25), (0.09, 0.2), (0.0, 0.155), (-0.09, 0.18), (-0.19, 0.23), (-0.27, 0.2), (-0.21, 0.11), (-0.12, 0.06), (-0.12, -0.06), (-0.16, -0.08), (-0.24, -0.12), (-0.2, -0.18), (-0.08, -0.165), (0.03, -0.2), (0.15, -0.26), (0.3, -0.24), (0.38, -0.14)]
def build(C, variant=None):
    yb = 0.19
    P = [C.shape_profile('fb_body', JAZZ, 0.05, yb, 0, bevel=0.02)]
    guard = [(0.0+(x-0.0)*0.8, z*0.8) for x, z in JAZZ]
    P.append(C.shape_profile('fb_guard', [(x, z) for x, z in guard if x < 0.24], 0.006, yb-0.006, 2, bevel=0.002))
    for x in (0.0, 0.14): P.append(C.prim('cube', 4, loc=(x,yb-0.012,0.0), scale=(0.04,0.01,0.16), bevel=0.01))
    P.append(bar(C, (0.20,-0.15), (0.34,-0.09), 0.06, 0.008, 5, yb-0.01, bevel=0.01))
    for x, z in ((0.23,-0.14),(0.31,-0.10)): P.append(C.prim('cyl', 5, loc=(x,yb-0.018,z), rot=(math.pi/2,0,0), scale=(0.018,0.018,0.016), verts=16))
    P.append(C.prim('cube', 5, loc=(0.24,0.04,0.02), scale=(0.07,0.30,0.03), bevel=0.006))          # bridge
    P.append(C.prim('cube', 4, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))
    P.append(C.prim('cube', 3, loc=(-0.52,yb-0.006,0.0), scale=(0.80,0.05,0.075), bevel=0.008))     # long ebony fretless board
    for i in range(10): P.append(C.prim('cube', 4, loc=(-0.20-0.07*i,yb-0.029,0.0), scale=(0.004,0.004,0.08)))
    P.append(C.shape_profile('fb_head', [(-0.92,-0.04),(-1.14,-0.03),(-1.18,0.03),(-1.12,0.09),(-0.96,0.085),(-0.92,0.04)], 0.05, yb, 0, bevel=0.012))
    for i in range(4):
        P.append(C.prim('cyl', 5, loc=(-0.97-0.05*i,yb,0.10+0.004*i), scale=(0.014,0.014,0.05), verts=12))
        P.append(C.prim('cyl', 5, loc=(-0.97-0.05*i,yb-0.03,0.04), rot=(math.pi/2,0,0), scale=(0.015,0.015,0.01), verts=12))
    P += strings(C, (-0.075,-0.025,0.025,0.075), 1, 0.016, 0.0018)
    return P
