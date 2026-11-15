"""french_horn (jewelbox 37): lead-pipe striker + round coils, rotary valves, side bell."""
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
def sweep(C, mi, pts, radii, y=0.22, ymax=0.058, n=24, cap0=True, cap1=True, name='tube'):
    """tube along an XZ polyline pts=[(x,z)...] (radius per point or one float); Y radius clamped to ymax"""
    rings = []
    for i, (x, z) in enumerate(pts):
        a = pts[max(i-1, 0)]; b = pts[min(i+1, len(pts)-1)]
        tx, tz = b[0]-a[0], b[1]-a[1]; L = math.hypot(tx, tz) or 1.0; tx, tz = tx/L, tz/L; nx, nz = -tz, tx
        r = radii[i] if isinstance(radii, (list, tuple)) else radii; ry = min(r, ymax)
        rings.append([(x + r*nx*math.cos(t), y + ry*math.sin(t), z + r*nz*math.cos(t)) for t in [2*math.pi*k/n for k in range(n)]])
    return _ring_mesh(C, name, rings, mi, cap0, cap1)
def arc_pts(cx, cz, R, a0, a1, m=16):
    return [(cx + R*math.cos(a0 + (a1-a0)*k/m), cz + R*math.sin(a0 + (a1-a0)*k/m)) for k in range(m+1)]
def bell(C, mi, dark, p0, d, L, r0, r1, y=0.22, ymax=0.058, power=3.0, m=18, name='bell'):
    """flared bell from p0 along direction d (XZ), length L, throat r0 -> rim r1; dark disc just inside the rim"""
    dl = math.hypot(*d); dx, dz = d[0]/dl, d[1]/dl
    pts = [(p0[0] + dx*L*k/m, p0[1] + dz*L*k/m) for k in range(m+1)]
    rad = [r0 + (r1-r0)*(k/m)**power for k in range(m+1)]
    o = [sweep(C, mi, pts, rad, y, ymax, n=32, cap0=False, cap1=False, name=name)]
    e = (p0[0] + dx*L*0.97, p0[1] + dz*L*0.97); r = r0 + (r1-r0)*0.97**power
    o.append(sweep(C, dark, [(e[0]-dx*0.004, e[1]-dz*0.004), e], r*0.96, y, ymax*0.96, n=32, name=name+'_m'))
    return o
def front_bell(C, mi, dark, x, z, r, y0=0.165, depth=0.11, r0=0.02, m=14, n=40, name='fbell'):
    """bell facing the camera (axis -Y): rim radius r at y0, throat r0 at y0+depth"""
    rings = []
    for k in range(m+1):
        t = k/m; rr = r0 + (r-r0)*(1-t)**3; yy = y0 + depth*t
        rings.append([(x + rr*math.cos(a), yy, z + rr*math.sin(a)) for a in [2*math.pi*j/n for j in range(n)]])
    o = [_ring_mesh(C, name, rings, mi, angle=1.2)]
    rr = r*0.55; yy = y0 + 0.035
    o.append(_ring_mesh(C, name+'_m', [[(x + rr*math.cos(a), yy, z + rr*math.sin(a)) for a in [2*math.pi*j/n for j in range(n)]]], dark, cap0=True))
    return o

def build(C, variant=None):
    P = [C.prim('cyl', 0, loc=(0,0,0.015), rot=(0,math.pi/2,0), scale=(0.03,0.03,0.62), verts=32)]
    cx, cz = -0.02, -0.27
    for R, r in ((0.21,0.018), (0.175,0.016), (0.14,0.015)):
        P.append(sweep(C, 0, arc_pts(cx,cz,R,0.0,2*math.pi,40), r, y=0.215, n=16))
    for i, x in enumerate((-0.07,-0.01,0.05)):
        P.append(C.prim('cyl', 0, loc=(x,0.2,-0.24), rot=(math.pi/2,0,0), scale=(0.028,0.028,0.07), verts=24))
        P.append(C.prim('cyl', 1, loc=(x,0.163,-0.24), rot=(math.pi/2,0,0), scale=(0.016,0.016,0.006), verts=16))
        P.append(bar(C, (x,-0.24), (x-0.10,-0.16+0.02*i), 0.012, 0.008, 1, 0.168))
        P.append(C.prim('cube', 1, loc=(x-0.10,0.168,-0.16+0.02*i), scale=(0.035,0.01,0.02), bevel=0.004))
    P.append(sweep(C, 0, [(0.31,0.015),(0.36,-0.03),(0.30,-0.07),(0.12,-0.08)], 0.02, y=0.2))          # lead pipe into the coils
    P += bell(C, 0, 2, (0.17,-0.42), (0.35,-1), 0.32, 0.02, 0.19, y=0.225, ymax=0.06)   # angled down so the rim stays in the showcase frame
    return P
