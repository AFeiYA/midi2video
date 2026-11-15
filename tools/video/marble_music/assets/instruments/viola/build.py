"""viola (jewelbox 26): steel strings striker + viola face-on with a bow behind the marble plane."""
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

def fiddle(C, L, y, mi, eb, dk, st, pale, cx=0.0, cz=0.0, rot=0.0, endpin=0.0, pin_mi=None, bstrings=True, chin=False, slope=False, name='fid'):
    """violin-family instrument (body length L) modelled horizontally - neck toward -x, body centred at x=0, front face at y -
    then rotated by rot about Y (rot = pi/2 stands it upright, neck up) and moved to (cx, cz).
    mi body, eb ebony (fingerboard/tailpiece/pegs), dk dark (f-holes, purfling), st strings, pale bridge."""
    import bpy
    ins = violin_inside(L, 0.0)
    if slope:                                                                           # double bass: sloping shoulders
        base = ins
        def ins(x, z, base=base):
            if x < -0.02*L and x > -0.47*L:
                lim = 0.12*L + (0.20*L)*(x+0.47*L)/(0.45*L)
                if abs(z) > lim and x < -0.25*L: return False
            return base(x, z)
    d = 0.03 + 0.03*L; P = [plate(C, name+'_b', ins, y, d, mi, n=180, bevel=0.01)]
    P.append(plate(C, name+'_e', ins, y+0.004, d*0.8, dk, n=180, bevel=0.0)); P[-1].scale = (1.02, 1.0, 1.03)
    for s in (-1, 1):
        P.append(bar(C, (0.03*L,s*0.09*L), (0.17*L,s*0.13*L), 0.016*L, 0.005, dk, y-0.004))
        for xx, zz in ((0.03*L,0.085*L), (0.18*L,0.135*L)): P.append(C.prim('cyl', dk, loc=(xx,y-0.004,s*zz), rot=(math.pi/2,0,0), scale=(0.018*L,0.018*L,0.005), verts=10))
    P.append(C.prim('cube', eb, loc=(-0.38*L,y-0.012,0.0), scale=(0.80*L,0.014,0.10*L), bevel=0.004))      # fingerboard
    P.append(C.prim('cube', mi, loc=(-0.88*L,y,0.0), scale=(0.16*L,0.03,0.09*L), bevel=0.006))             # pegbox
    P.append(C.prim('torus', mi, loc=(-0.98*L,y,0.0), rot=(math.pi/2,0,0), scale=(0.05*L,0.022*L), verts=24))  # scroll
    P.append(C.prim('sphere', mi, loc=(-0.98*L,y,0.0), scale=(0.035*L,0.012,0.035*L), verts=16))
    for xx in (-0.84*L, -0.92*L):
        for s in (-1, 1): P.append(C.prim('cyl', eb, loc=(xx,y,s*0.09*L), scale=(0.012*L+0.004,0.012*L+0.004,0.07*L), verts=10))
    P.append(C.shape_profile(name+'_tp', [(0.26*L,-0.05*L),(0.44*L,-0.03*L),(0.44*L,0.03*L),(0.26*L,0.05*L)], 0.012, y-0.016, eb, bevel=0.004))
    if bstrings:
        P.append(C.prim('cube', pale, loc=(0.10*L,y-0.016,0.0), scale=(0.02,0.012,0.14*L), bevel=0.003))     # bridge
        for z in (-0.045*L,-0.015*L,0.015*L,0.045*L):
            P.append(C.prim('cyl', st, loc=(-0.25*L,y-0.022,z), rot=(0,math.pi/2,0), scale=(0.0025+0.002*L,0.0025+0.002*L,1.08*L), verts=8))
    if chin: P.append(C.prim('sphere', eb, loc=(0.36*L,y-0.01,0.13*L), scale=(0.07*L,0.012,0.05*L), verts=16))
    if endpin > 0:
        P.append(C.prim('cyl', pin_mi if pin_mi is not None else st, loc=(0.47*L+endpin/2,y,0.0), rot=(0,math.pi/2,0), scale=(0.008,0.008,endpin), verts=10))
        P.append(C.prim('cyl', eb, loc=(0.47*L,y,0.0), rot=(0,math.pi/2,0), scale=(0.02,0.02,0.04), verts=12))
    o = C.join(P, name); o.rotation_euler = (0, rot, 0); o.location = (cx, 0, cz)
    C._activate(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o
def bow(C, stick, hair, frog, tip, y=0.0, x0=-0.31, x1=0.31, top=0.045, depth=0.05, pearl=None):
    """bow as a striker (inside the contact rectangle): stick (top flush with the contact face), hair ribbon below, frog + tip"""
    r = 0.018; P = [C.prim('cyl', stick, loc=((x0+x1)/2,y,top-r), rot=(0,math.pi/2,0), scale=(r,r,x1-x0-0.02), verts=16)]
    P.append(C.prim('cube', hair, loc=((x0+x1)/2+0.02,y,top-0.068), scale=(x1-x0-0.10,depth,0.008)))
    P.append(C.prim('cube', frog, loc=(x0+0.05,y,top-0.05), scale=(0.08,depth+0.02,0.07), bevel=0.008))      # frog
    if pearl is not None: P.append(C.prim('cyl', pearl, loc=(x0+0.05,y-depth/2-0.011,top-0.05), rot=(math.pi/2,0,0), scale=(0.012,0.012,0.004), verts=12))
    P.append(C.shape_profile('bow_tip', [(x1-0.05,top-0.072),(x1,top-0.072),(x1,top-0.004),(x1-0.02,top)], depth+0.01, y-(depth+0.01)/2, tip, bevel=0.003))
    return P
def back_bow(C, a, b, y, stick, hair, frog):
    """bow drawn behind the marble plane from (x,z) a (frog) to b (tip)"""
    P = [rod(C, (a[0],a[1],y), b, 0.008, stick)]
    dx, dz = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dz); nx, nz = dz/L, -dx/L
    P.append(rod(C, (a[0]+0.03*nx+0.05*dx/L, a[1]+0.03*nz+0.05*dz/L, y+0.004), (b[0]+0.02*nx, b[1]+0.02*nz), 0.006, hair, verts=8))
    P.append(bar(C, (a[0], a[1]), (a[0]+0.06*dx/L, a[1]+0.06*dz/L), 0.04, 0.02, frog, y, bevel=0.004))
    return P

def build(C, variant=None):
    P = [fiddle(C, 0.64, 0.20, 0, 1, 2, 3, 4, cx=0.02, bstrings=False, chin=True)]
    P += back_bow(C, (0.55, 0.3), (-0.5, -0.26), 0.172, 5, 6, 1)
    P.append(C.prim('cube', 4, loc=(0.12,0.04,0.015), scale=(0.025,0.30,0.035), bevel=0.004))      # bridge (in the contact rectangle)
    P.append(C.prim('cube', 1, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))                   # nut
    P += strings(C, (-0.075,-0.025,0.025,0.075), 3, 0.009, 0.0008)
    return P
