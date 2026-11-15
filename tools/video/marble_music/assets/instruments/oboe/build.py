"""oboe (jewelbox 42)."""
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

def _ring_mesh(C, name, rings, mi, cap0=False, cap1=False, angle=1.0):
    import bpy, bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in ring] for ring in rings]; n = len(rings[0])
    for a, b in zip(vs[:-1], vs[1:]):
        for i in range(n): bm.faces.new((a[i], a[(i+1)%n], b[(i+1)%n], b[i]))
    if cap0: bm.faces.new(vs[0][::-1])
    if cap1: bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); C._ensure_slots(o)
    for p in me.polygons: p.material_index = mi
    C.shade_by_angle(o, angle); return o
def _v(a, b, s=1.0): return (a[0]+s*b[0], a[1]+s*b[1], a[2]+s*b[2])
def _sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def _dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def _cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def _unit(a):
    L = math.sqrt(_dot(a, a)) or 1.0; return (a[0]/L, a[1]/L, a[2]/L)
def _smooth(P, R, k):
    # centripetal Catmull-Rom through every point (k sub-steps per segment): bends become round instead of cracked polyline corners
    if k <= 1 or len(P) < 3: return P, R
    E = [_v(P[0], _sub(P[0], P[1]))] + list(P) + [_v(P[-1], _sub(P[-1], P[-2]))]
    oP, oR = [], []
    for i in range(1, len(E)-2):
        p0, p1, p2, p3 = E[i-1], E[i], E[i+1], E[i+2]
        d = lambda a, b: max(math.sqrt(_dot(_sub(a, b), _sub(a, b)))**0.5, 1e-6)
        t0 = 0.0; t1 = t0+d(p0, p1); t2 = t1+d(p1, p2); t3 = t2+d(p2, p3)
        for s in range(k):
            t = t1 + (t2-t1)*s/k
            L = lambda a, b, ta, tb: tuple(((tb-t)*a[c] + (t-ta)*b[c])/(tb-ta) for c in range(3))
            A1 = L(p0, p1, t0, t1); A2 = L(p1, p2, t1, t2); A3 = L(p2, p3, t2, t3)
            B1 = L(A1, A2, t0, t2); B2 = L(A2, A3, t1, t3)
            oP.append(L(B1, B2, t1, t2)); oR.append(R[i-1] + (R[i]-R[i-1])*s/k)
    return oP + [P[-1]], oR + [R[-1]]
def tube3(C, mi, pts, radii, n=24, ymax=None, cap0=True, cap1=True, name='tube', smooth=4, angle=1.0):
    # one continuous swept tube along a 3-D path (rotation-minimising frames); Y offsets squashed to ymax when r > ymax
    R = list(radii) if isinstance(radii, (list, tuple)) else [radii]*len(pts)
    P, R = _smooth([tuple(p) for p in pts], R, smooth)
    T = [_unit(_sub(P[min(i+1, len(P)-1)], P[max(i-1, 0)])) for i in range(len(P))]
    ref = (0.0, 1.0, 0.0) if abs(T[0][1]) < 0.9 else (1.0, 0.0, 0.0)
    N = _unit(_cross(ref, T[0])); rings = []
    for i, p in enumerate(P):
        if i: N = _unit(_sub(N, tuple(T[i][c]*_dot(N, T[i]) for c in range(3))))
        Bv = _cross(T[i], N); r = R[i]; sq = (ymax/r) if (ymax is not None and r > ymax) else 1.0
        ring = []
        for k in range(n):
            a = 2*math.pi*k/n; o = tuple(r*(N[c]*math.cos(a) + Bv[c]*math.sin(a)) for c in range(3))
            ring.append((p[0]+o[0], p[1]+o[1]*sq, p[2]+o[2]))
        rings.append(ring)
    return _ring_mesh(C, name, rings, mi, cap0, cap1, angle)
def sweep(C, mi, pts, radii, y=0.22, ymax=0.058, n=24, cap0=True, cap1=True, name='tube', smooth=4):
    # tube along an XZ polyline at depth y (points may also be (x,y,z)); smoothed through the points
    P = [(p[0], y, p[1]) if len(p) == 2 else tuple(p) for p in pts]
    return tube3(C, mi, P, radii, n=n, ymax=ymax, cap0=cap0, cap1=cap1, name=name, smooth=smooth)
def arc_pts(cx, cz, R, a0, a1, m=16):
    return [(cx + R*math.cos(a0 + (a1-a0)*k/m), cz + R*math.sin(a0 + (a1-a0)*k/m)) for k in range(m+1)]
def elbow_pts(side, zc, r, y1, x_edge=0.31, m=10, lead=0.03):
    # 3-D path that leaves the striker tube end (local y=0, axis z=zc, radius r) and folds back into the backplate band WITHOUT
    # leaving |x|<=x_edge inside the marble slab: bend +Y at x=side*(x_edge-r), run back, bend outward again at depth y1.
    # Ends at (side*(x_edge-r+Rb), y1, zc) heading outward (side*+X).
    Rb = 1.3*r; xc = x_edge - r; y1 = max(y1, 0.157 + Rb); pts = [(side*(xc-Rb-lead), 0.0, zc)]
    for k in range(m+1):
        a = 0.5*math.pi*k/m; pts.append((side*(xc-Rb+Rb*math.sin(a)), Rb-Rb*math.cos(a), zc))
    for k in range(m+1):
        a = 0.5*math.pi*k/m; pts.append((side*(xc+Rb-Rb*math.cos(a)), y1-Rb+Rb*math.sin(a), zc))
    return pts, y1
def chain(C, mi, side, zc, r, y1, cont=(), radii=None, n=24, ymax=0.058, cap1=True, name='chain'):
    # striker-end elbow + continuation polyline (x,z) at depth y1 as ONE continuous mesh. Returns (obj, (x_exit, y1)).
    E, y1 = elbow_pts(side, zc, r, y1); ex = E[-1][0]
    C2 = [(x, z) for x, z in cont]
    R2 = [r]*len(C2) if radii is None else ([radii]*len(C2) if not isinstance(radii, (list, tuple)) else list(radii))
    while C2 and side*C2[0][0] <= side*ex + 0.004: C2.pop(0); R2.pop(0)
    if not C2: C2, R2 = [(ex + side*0.006, zc)], [r]                       # stub past the exit so the next mesh overlaps (no seam)
    rr = [r]*len(E) + R2
    P = E + [(x, y1, z) for x, z in C2]
    # elbow points are already dense: smooth only lightly
    return tube3(C, mi, P, rr, n=n, ymax=ymax, cap0=True, cap1=cap1, name=name, smooth=2), (ex, y1)
def yport(C, mi, x, z, r, y0=0.0, y1=0.2, verts=20):
    # short straight tube along +Y joining a striker part to something in the backplate band (valve casings, braces, ties)
    return C.prim('cyl', mi, loc=(x, (y0+y1)/2, z), rot=(math.pi/2, 0, 0), scale=(r, r, y1-y0), verts=verts)
def collar(C, mi, x, z, y, r, w=0.012, d=(1,0), ymax=0.06):
    # ferrule ring covering a join between two tube meshes (centre (x,z) at depth y, along direction d)
    L = math.hypot(*d); dx, dz = d[0]/L, d[1]/L
    return sweep(C, mi, [(x-dx*w/2, z-dz*w/2), (x+dx*w/2, z+dz*w/2)], r, y=y, ymax=ymax, n=32, smooth=1)
def bell(C, mi, dark, p0, d, L, r0, r1, y=0.22, ymax=0.058, power=3.0, m=18, name='bell', d0=None):
    # flared bell from p0 along direction d (XZ), length L, throat r0 -> rim r1; dark disc just inside the rim.
    # d0: direction of the tube feeding the bell - the bell axis bends smoothly from d0 to d (quadratic Bezier) so the join has no kink;
    # the throat starts 4 mm back inside the feeding tube so the meshes overlap instead of leaving a seam.
    dl = math.hypot(*d); dx, dz = d[0]/dl, d[1]/dl
    if d0 is None: d0 = d
    l0 = math.hypot(*d0); ux, uz = d0[0]/l0, d0[1]/l0
    q0 = (p0[0] - ux*0.004, p0[1] - uz*0.004); q1 = (p0[0] + ux*L*0.45, p0[1] + uz*L*0.45); q2 = (q1[0] + dx*L*0.55, q1[1] + dz*L*0.55)
    B = lambda t: tuple((1-t)**2*q0[c] + 2*(1-t)*t*q1[c] + t*t*q2[c] for c in range(2))
    pts = [B(k/m) for k in range(m+1)]
    rad = [r0 + (r1-r0)*(k/m)**power for k in range(m+1)]
    o = [sweep(C, mi, pts, rad, y, ymax, n=32, cap0=False, cap1=False, name=name, smooth=1)]
    e = B(0.97); r = r0 + (r1-r0)*0.97**power
    o.append(sweep(C, dark, [(e[0]-dx*0.004, e[1]-dz*0.004), e], r*0.96, y, ymax*0.96, n=32, name=name+'_m', smooth=1))
    return o
def front_bell(C, mi, dark, x, z, r, y0=0.165, depth=0.11, r0=0.02, m=14, n=40, name='fbell'):
    # bell facing the camera (axis -Y): rim radius r at y0, throat r0 at y0+depth
    rings = []
    for k in range(m+1):
        t = k/m; rr = r0 + (r-r0)*(1-t)**3; yy = y0 + depth*t
        rings.append([(x + rr*math.cos(a), yy, z + rr*math.sin(a)) for a in [2*math.pi*j/n for j in range(n)]])
    o = [_ring_mesh(C, name, rings, mi, angle=1.2)]
    rr = r*0.55; yy = y0 + 0.035
    o.append(_ring_mesh(C, name+'_m', [[(x + rr*math.cos(a), yy, z + rr*math.sin(a)) for a in [2*math.pi*j/n for j in range(n)]]], dark, cap0=True))
    return o

def tube_x(C, mi, r, x0=-0.31, x1=0.31, zc=None, verts=40):
    zc = 0.045 - r if zc is None else zc
    return C.prim('cyl', mi, loc=((x0+x1)/2,0,zc), rot=(0,math.pi/2,0), scale=(r,r,x1-x0), verts=verts)
def ferrule(C, mi, x, r, zc, w=0.014, extra=0.004):
    """metal ring around a tube of radius r at axis z=zc; top stays flush with the tube top"""
    return C.prim('cyl', mi, loc=(x,0,zc-extra), rot=(0,math.pi/2,0), scale=(r+extra,r+extra,w), bevel=0.002, verts=40)
def hole(C, mi, x, r, zc, rh=0.011):
    """dark tone hole on the camera side (-Y) of a tube"""
    return C.prim('cyl', mi, loc=(x,-(r-0.004),zc), rot=(math.pi/2,0,0), scale=(rh,rh,0.012), verts=20)
def keycup(C, mi, x, r, zc, rc=0.017, pad=None):
    o = [C.prim('cyl', mi, loc=(x,-(r+0.002),zc), rot=(math.pi/2,0,0), scale=(rc,rc,0.008), bevel=0.002, verts=24)]
    if pad is not None: o.append(C.prim('cyl', pad, loc=(x,-(r+0.0065),zc), rot=(math.pi/2,0,0), scale=(rc*0.62,rc*0.62,0.003), verts=20))
    return o
def keyrod(C, mi, r, zc, x0=-0.28, x1=0.28, dz=-0.6, rr=0.0035):
    return C.prim('cyl', mi, loc=((x0+x1)/2,-r*0.78,zc+dz*r), rot=(0,math.pi/2,0), scale=(rr,rr,x1-x0), verts=8)
def double_reed(C, cork, thread, cane, x0, z, y=0.19, dirx=-1.0, scale=1.0, dirz=0.0):
    """staple + cork + coloured thread wrap + flat cane blades, pointing along (dirx, dirz) from (x0, z)"""
    s = scale; L = math.hypot(dirx, dirz); dx, dz = dirx/L, dirz/L; o = []
    p = lambda t: (x0+dx*t*s, z+dz*t*s)
    o.append(sweep(C, cork, [p(0), p(0.035)], [0.011*s,0.008*s], y=y))
    o.append(sweep(C, thread, [p(0.035), p(0.06)], [0.0085*s,0.0075*s], y=y))
    o.append(sweep(C, cane, [p(0.06), p(0.08), p(0.1), p(0.112)], [0.006*s,0.009*s,0.011*s,0.011*s], y=y, ymax=0.003*s))
    return o

def build(C, variant=None):
    r = 0.032; zc = 0.045 - r
    P = [tube_x(C, 0, r, zc=zc)]
    for x in (-0.30, -0.06, 0.30): P.append(ferrule(C, 1, x, r, zc))
    for x in (-0.24,-0.20,-0.15,-0.11,-0.02,0.03,0.08,0.13,0.18,0.23,0.27): P += keycup(C, 1, x, r, zc, rc=0.012)
    for x in (-0.175,0.105): P.append(hole(C, 2, x, r, zc, 0.007))
    P.append(keyrod(C, 1, r, zc, dz=-0.55)); P.append(keyrod(C, 1, r, zc, -0.26, 0.20, dz=0.35, rr=0.0028))
    for x in (-0.22,-0.13,0.0,0.10,0.20): P.append(C.prim('cube', 1, loc=(x,-r*0.85,zc-0.012), scale=(0.004,0.006,0.02)))   # posts
    o, (bx, by) = chain(C, 0, 1, zc, r, 0.195); P.append(o)                                                # body folds back into the bell
    P += bell(C, 0, 2, (bx,zc), (1,0), 0.09, r, 0.05, y=by, ymax=0.036, power=2.5)
    P.append(sweep(C, 1, [(bx+0.085,zc),(bx+0.093,zc)], 0.052, y=by, ymax=0.037, smooth=1))
    o, (mx, my) = chain(C, 0, -1, zc, r, 0.195); P.append(o)
    P.append(collar(C, 1, mx-0.003, zc, my, 0.035, w=0.012, ymax=0.036))
    P.append(sweep(C, 1, [(mx,zc),(mx-0.03,zc)], [0.018,0.012], y=my))                                     # reed well
    P += double_reed(C, 3, 4, 5, mx-0.03, zc, y=my, scale=1.15)
    return P
