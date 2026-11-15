"""voice_oohs (jewelbox 31): chrome boom striker + vintage art-deco microphone on a stand."""
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
    P = [C.prim('cyl', 0, loc=(0.02,0.0,0.007), rot=(0,math.pi/2,0), scale=(0.038,0.038,0.56), verts=32)]   # boom arm (top z=0.045)
    P.append(C.prim('sphere', 0, loc=(-0.262,0.0,0.0), scale=(0.045,0.045,0.045), verts=24))         # counterweight
    P.append(C.prim('cube', 3, loc=(-0.08,0.0,0.0), scale=(0.07,0.10,0.07), bevel=0.01))           # boom clamp
    # microphone capsule on a yoke at the right end
    mx, mz = 0.47, 0.16
    P.append(bar(C, (0.30,0.007), (mx,mz-0.19), 0.03, 0.03, 0, 0.2, bevel=0.008))
    P.append(C.prim('torus', 2, loc=(mx,0.21,mz-0.02), rot=(math.pi/2,0,0), scale=(0.15,0.014), verts=40))
    P.append(C.prim('sphere', 0, loc=(mx,0.225,mz), scale=(0.13,0.055,0.19), verts=40))
    for k in range(-5, 6):
        dz = 0.028*k; w = 2*0.13*math.sqrt(max(0.0, 1-(dz/0.19)**2))*0.82
        if w > 0.03: P.append(C.prim('cube', 1, loc=(mx,0.168+0.04*(abs(dz)/0.19)**2,mz+dz), scale=(w,0.006,0.011), bevel=0.002))
    P.append(C.prim('cube', 2, loc=(mx,0.163,mz), scale=(0.02,0.008,0.37), bevel=0.004))          # gold spine
    # stand: chrome pole from the clamp down to a black cast base
    P.append(C.prim('cyl', 0, loc=(-0.08,0.21,-0.32), scale=(0.018,0.018,0.64), verts=16))
    P.append(C.prim('cyl', 3, loc=(-0.08,0.22,-0.64), scale=(0.18,0.055,0.04), verts=40))
    P.append(C.prim('cyl', 0, loc=(-0.08,0.21,-0.10), scale=(0.03,0.03,0.05), verts=16))
    for i in range(10): P.append(C.prim('torus', 3, loc=(0.0,0.19,-0.08-0.05*i), rot=(math.pi/2,0,0), scale=(0.014,0.005), verts=12))   # cable
    P.append(C.prim('cube', 3, loc=(-0.48,0.25,0.22), scale=(0.24,0.05,0.09), bevel=0.012))        # ON-AIR lamp
    P.append(C.prim('cube', 4, loc=(-0.48,0.222,0.22), scale=(0.20,0.006,0.06), bevel=0.006))
    return P
