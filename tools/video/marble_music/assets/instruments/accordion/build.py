"""accordion (jewelbox 15): key + face-on red pearl accordion (grille, bellows, bass buttons)."""
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
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.70,0.12,0.06), bevel=0.008))          # red pearl key bed
    P += stubs(C, variant, 3)
    zc, hz = -0.25, 0.34
    # treble box (left) with grille
    P.append(C.prim('cube', 1, loc=(-0.42,0.23,zc), scale=(0.30,0.12,hz), bevel=0.025))
    P.append(C.prim('cube', 3, loc=(-0.42,0.168,zc), scale=(0.24,0.006,hz-0.07)))
    X0, X1, Z0, Z1 = -0.53, -0.31, zc-0.13, zc+0.13                                                # diamond lattice clipped to the grille
    for sgn in (1, -1):
        for k in range(-8, 9):
            c = 0.05*k; seg = []                                                                    # line z - zc = sgn*(x - (-0.42)) + c
            for x in (X0, X1):
                z = zc + sgn*(x+0.42) + c
                if Z0 <= z <= Z1: seg.append((x, z))
            for z in (Z0, Z1):
                x = -0.42 + sgn*(z - zc - c)
                if X0 <= x <= X1: seg.append((x, z))
            seg = sorted(set((round(x,5), round(z,5)) for x, z in seg))
            if len(seg) >= 2 and math.hypot(seg[-1][0]-seg[0][0], seg[-1][1]-seg[0][1]) > 0.02:
                P.append(bar(C, seg[0], seg[-1], 0.008, 0.008, 2, 0.163))
    # trim the lattice visually with a chrome frame
    P.append(C.prim('cube', 2, loc=(-0.42,0.162,zc+hz/2-0.03), scale=(0.25,0.006,0.012)))
    P.append(C.prim('cube', 2, loc=(-0.42,0.162,zc-hz/2+0.03), scale=(0.25,0.006,0.012)))
    # bellows: alternating pleats
    for i in range(13):
        x = -0.255 + 0.04*i
        P.append(C.prim('cube', 3 if i % 2 == 0 else 4, loc=(x,0.22,zc), scale=(0.04,0.10,hz-0.02), bevel=0.004))
    for x in (-0.25, 0.23):
        for z in (zc+hz/2-0.02, zc-hz/2+0.02):
            P.append(C.prim('cube', 2, loc=(x,0.168,z), scale=(0.03,0.01,0.03), bevel=0.004))
    # bass box (right) with buttons + strap
    P.append(C.prim('cube', 1, loc=(0.40,0.23,zc), scale=(0.28,0.12,hz), bevel=0.025))
    for r in range(5):
        for c in range(4):
            P.append(C.prim('sphere', 5 if (r+c) % 3 else 3, loc=(0.32+0.05*c+0.012*r,0.168,zc-0.11+0.055*r), scale=(0.016,0.01,0.016), verts=12))
    P.append(C.prim('cube', 3, loc=(0.54,0.16,zc), scale=(0.025,0.01,hz-0.06), bevel=0.004))       # strap
    return P
