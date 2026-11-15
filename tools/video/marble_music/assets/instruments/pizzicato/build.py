"""pizzicato (jewelbox 23): gut strings + three fanned small violins (string section, no bow)."""
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

def violin(C, cx, cz, ang, y, mi, L=0.48):
    import mathutils
    parts = [plate(C, 'pz_v', violin_inside(L, 0.0), y, 0.035, mi, n=140, bevel=0.008)]
    parts.append(C.prim('cube', 2, loc=(-0.26*L/0.4,y-0.008,0.0), scale=(0.40*L/0.4,0.012,0.04), bevel=0.004))
    for s in (-1, 1): parts.append(bar(C, (0.0,s*0.035), (0.06,s*0.05), 0.008, 0.004, 5, y-0.003))
    parts.append(C.prim('torus', mi, loc=(-0.42*L/0.4,y,0.0), rot=(math.pi/2,0,0), scale=(0.022,0.011), verts=20))
    parts.append(C.prim('cube', 2, loc=(0.17*L/0.4,y-0.008,0.0), scale=(0.08,0.012,0.04), bevel=0.004))    # tailpiece
    o = C.join(parts, 'pz_violin'); o.rotation_euler = (0, -ang, 0); o.location = (cx, 0, cz)
    C._activate(o); __import__('bpy').ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o
def build(C, variant=None):
    P = [violin(C, 0.05, 0.12, 0.35, 0.235, 3), violin(C, 0.08, -0.12, -0.35, 0.215, 4), violin(C, -0.02, 0.0, 0.0, 0.19, 0)]
    P.append(C.prim('cube', 3, loc=(0.18,0.04,0.015), scale=(0.025,0.30,0.035), bevel=0.004))       # bridge (in the contact rectangle)
    P.append(C.prim('cube', 2, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))
    P += strings(C, (-0.075,-0.025,0.025,0.075), 1, 0.010, 0.001)
    return P
