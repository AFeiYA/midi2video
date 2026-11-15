"""choir (jewelbox 30): oak riser striker + two rows of robed singers."""
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

def singer(C, cx, z0, y, h=0.26, s=1.0, hair_mi=4):
    w0, w1 = 0.065*s, 0.095*s; P = []
    P.append(C.shape_profile('robe', [(cx-w1,z0),(cx+w1,z0),(cx+w0,z0+h),(cx+w0*0.6,z0+h+0.02*s),(cx-w0*0.6,z0+h+0.02*s),(cx-w0,z0+h)], 0.05, y, 1, bevel=0.012))
    for sg in (-1, 1): P.append(bar(C, (cx+sg*0.045*s, z0+h+0.01), (cx+sg*0.012*s, z0+h*0.45), 0.022*s, 0.006, 2, y-0.004))
    P.append(C.prim('cube', 5, loc=(cx, y-0.012, z0+h*0.55), scale=(0.09*s,0.012,0.07*s), bevel=0.004))      # folder
    hz = z0+h+0.065*s
    P.append(C.prim('sphere', 3, loc=(cx,y+0.02,hz), scale=(0.048*s,0.03,0.052*s), verts=24))              # head
    P.append(C.prim('sphere', hair_mi, loc=(cx,y+0.03,hz+0.014*s), scale=(0.052*s,0.03,0.048*s), verts=24))  # hair (behind/above)
    P.append(C.prim('cyl', 4, loc=(cx,y-0.012,hz-0.018*s), rot=(math.pi/2,0,0), scale=(0.012*s,0.016*s,0.006), verts=12))   # open "aah" mouth
    for sg in (-1, 1): P.append(C.prim('sphere', 4, loc=(cx+sg*0.017*s,y-0.01,hz+0.008*s), scale=(0.006*s,0.004,0.006*s), verts=8))
    return P
def build(C, variant=None):
    P = [C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.012)]
    P.append(C.prim('cube', 0, loc=(0,0.23,-0.03), scale=(1.20,0.14,0.07), bevel=0.01))            # riser step behind (front row stands here)
    P.append(C.prim('cube', 0, loc=(0,0.27,0.04), scale=(1.10,0.06,0.09), bevel=0.01))             # second step (back row)
    P.append(C.prim('cube', 6, loc=(0,0.159,-0.055), scale=(1.20,0.008,0.014)))
    for cx in (-0.34, -0.12, 0.12, 0.34): P += singer(C, cx, 0.09, 0.262, s=0.92)
    for cx in (-0.50, -0.27, 0.27, 0.50): P += singer(C, cx, 0.0, 0.205)
    return P
