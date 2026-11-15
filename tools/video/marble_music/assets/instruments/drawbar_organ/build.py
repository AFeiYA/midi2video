"""drawbar_organ (jewelbox 13): key + drawbar bank + walnut tonewheel console with pedalboard."""
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

def build(C, variant='white'):
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.70,0.12,0.06), bevel=0.008))          # walnut key bed
    P += stubs(C, variant, 5)
    # drawbar bank (left of the keys): housing + 9 rods pulled to different lengths, tab colours brown brown white white black white black black white
    P.append(C.prim('cube', 1, loc=(-0.50,0.25,0.02), scale=(0.30,0.07,0.10), bevel=0.01))
    cols = [3,3,4,4,5,4,5,5,4]; Ls = [0.08,0.13,0.16,0.06,0.12,0.03,0.10,0.05,0.14]
    for i, (c, L) in enumerate(zip(cols, Ls)):
        x = -0.62 + 0.03*i
        P.append(C.prim('cyl', 2, loc=(x,0.22,0.07+L/2), scale=(0.006,0.006,L), verts=8))
        P.append(C.prim('cube', c, loc=(x,0.22,0.07+L+0.025), scale=(0.024,0.03,0.05), bevel=0.005))
    # console: walnut cabinet, chrome trim, two tapered legs, bass pedalboard
    P.append(C.prim('cube', 1, loc=(0,0.23,-0.19), scale=(1.12,0.12,0.22), bevel=0.02))
    P.append(C.prim('cube', 2, loc=(0,0.168,-0.085), scale=(1.10,0.008,0.012)))
    P.append(C.prim('cube', 1, loc=(0,0.20,-0.20), scale=(0.96,0.06,0.15), bevel=0.01))            # recessed front panel
    for x in (-0.50, 0.50):
        P.append(rod(C, (x,-0.30,0.22), (x*1.05,-0.52), 0.025, 1))
    for i in range(9):                                                                              # pedals fan out toward the player
        x = -0.32 + 0.08*i
        P.append(bar(C, (x*0.6,-0.40), (x,-0.53), 0.05, 0.03, 6 if i % 3 != 1 else 5, 0.20, bevel=0.006))
    P.append(C.prim('cube', 1, loc=(0,0.21,-0.555), scale=(0.84,0.08,0.025), bevel=0.006))
    return P
