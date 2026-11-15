"""shared build.py / material.py source snippets for the jewelbox generators (pasted into each asset's build.py)."""
H = '''
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
'''

IVORY = '''
def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.93,0.89,0.80),rough=0.16,coat=0.7)
'''

# brass / woodwind tubing: swept tubes along XZ polylines (cross-section flattened in Y so they stay in the backplate band),
# flared bells, camera-facing bells. Used by jewelbox_f4+ (paste after H).
BRASS = '''
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
'''

# woodwinds: body tube in the marble slab (top flush with the contact face), metal ferrules flush on top, camera-side tone holes / keys.
# Paste after H + BRASS (uses sweep).
WOOD = '''
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
'''
