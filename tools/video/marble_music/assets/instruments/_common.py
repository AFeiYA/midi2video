"""Shared helpers for the procedural instrument asset library (run inside Blender).
Local frame of every striker (must match plan_zigzag.py):
  +Z = paddle normal (marble side); the marble touches the point (0,0,+PT/2) = (0,0,0.045) on the hit frame
  X  = paddle tangent, contact face spans x in [-PL/2, PL/2] = [-0.31, 0.31]
  Y  = into the wall (camera at -Y). Marble occupies |y| <= R = 0.15. Wall plane is at y = WALL_Y = 0.30.
Anything outside the planner rectangle |x|<=0.31, |z|<=0.045 is 'decorative' and is checked by check_keepout.py."""
import bpy, math, json, os
PL, PT, R, WALL_Y = 0.62, 0.09, 0.15, 0.30
TOP = PT/2

def _activate(o):
    for s in bpy.context.selected_objects: s.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)

NSLOT = 8
def _ensure_slots(o, n=NSLOT):
    """placeholder material slots __slot0..__slot{n-1} (same datablocks on every part): Blender clamps material_index to the
    slot count whenever a modifier/transform is applied or objects are joined, so parts need real slots from creation."""
    me = o.data
    while len(me.materials) < n:
        i = len(me.materials); me.materials.append(bpy.data.materials.get(f'__slot{i}') or bpy.data.materials.new(f'__slot{i}'))

def prim(kind, mi=0, loc=(0,0,0), rot=(0,0,0), scale=(1,1,1), bevel=0.0, seg=3, verts=32, smooth=True, angle=0.6):
    """kind: cube (size 1), cyl (radius 1, depth 1 along local Z), sphere (radius 1), torus(major,minor in scale)."""
    if kind == 'cube': bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == 'cyl': bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=verts)
    elif kind == 'sphere': bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=verts, ring_count=max(8, verts//2))
    elif kind == 'torus': bpy.ops.mesh.primitive_torus_add(major_radius=scale[0], minor_radius=scale[1], major_segments=verts, minor_segments=12); scale = (1,1,1)
    o = bpy.context.object; _ensure_slots(o)
    o.location = loc; o.rotation_euler = rot; o.scale = scale
    _activate(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for p in o.data.polygons: p.material_index = mi
    if bevel > 0:
        m = o.modifiers.new('bev', 'BEVEL'); m.width = bevel; m.segments = seg; m.limit_method = 'ANGLE'
        bpy.ops.object.modifier_apply(modifier=m.name)
    if smooth: shade_by_angle(o, angle)
    return o

def _set_boolean_solver(mod):
    # Blender 4.2 has EXACT; 4.5+/5.x replaced it with MANIFOLD.
    for s in ('EXACT', 'MANIFOLD', 'FLOAT'):
        try:
            mod.solver = s
            return s
        except Exception:
            continue
    return None

def shade_by_angle(o, angle=0.6):
    """Smooth shading by edge angle. shade_smooth_by_angle is 4.1–4.5; 5.x prefers shade_auto_smooth."""
    _activate(o)
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=angle)
        return
    except Exception:
        pass
    try:
        bpy.ops.object.shade_auto_smooth(use_auto_smooth=True, angle=angle)
    except Exception:
        bpy.ops.object.shade_smooth()

def cut(o, cutter, mi=None):
    """Boolean difference; faces created from the cutter keep the cutter's material index (INDEX mode)."""
    if mi is not None:
        for p in cutter.data.polygons: p.material_index = mi
    m = o.modifiers.new('cut', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cutter
    try: m.material_mode = 'INDEX'
    except Exception: pass
    _set_boolean_solver(m)
    _activate(o); bpy.ops.object.modifier_apply(modifier=m.name); bpy.data.objects.remove(cutter, do_unlink=True); return o

def join(objs, name):
    _activate(objs[0])
    for o in objs: o.select_set(True)
    bpy.ops.object.join(); o = bpy.context.object; o.name = name; o.data.name = name; return o

def shape_profile(name, pts_xz, depth, y0, mi=0, bevel=0.0):
    """Extrude a closed XZ polygon (list of (x,z)) along Y from y0 to y0+depth."""
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts_xz]; b = [bm.verts.new((x, y0+depth, z)) for x, z in pts_xz]
    n = len(pts_xz); bm.faces.new(a[::-1]); bm.faces.new(b)
    for i in range(n): bm.faces.new((a[i], a[(i+1)%n], b[(i+1)%n], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); _ensure_slots(o)
    for p in me.polygons: p.material_index = mi
    if bevel > 0:
        _activate(o); m = o.modifiers.new('bev', 'BEVEL'); m.width = bevel; m.segments = 3; m.limit_method = 'ANGLE'; bpy.ops.object.modifier_apply(modifier=m.name)
    _activate(o); shade_by_angle(o, 0.6); return o

# ---------- materials
def mat(name, base, rough=0.5, metal=0.0, trans=0.0, ior=1.45, coat=0.0, coat_rough=0.03, aniso=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    b.inputs['Transmission Weight'].default_value = trans; b.inputs['IOR'].default_value = ior; b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = coat_rough; b.inputs['Anisotropic'].default_value = aniso
    return m

def add_wood(m, c1, c2, scale=6.0, rings=2.5):
    b = m.node_tree.nodes['Principled BSDF']; nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, scale*0.15, scale)
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'RINGS'; wv.inputs['Scale'].default_value = rings; wv.inputs['Distortion'].default_value = 6; wv.inputs['Detail'].default_value = 3
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    ad = nt.nodes.new('ShaderNodeMath'); ad.operation = 'ADD'; mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = 0.6
    L = nt.links.new
    L(tc.outputs['Object'], mp.inputs[0]); L(mp.outputs[0], wv.inputs[0]); L(mp.outputs[0], nz.inputs[0])
    L(wv.outputs['Fac'], ad.inputs[0]); L(nz.outputs['Fac'], ad.inputs[1]); L(ad.outputs[0], mu.inputs[0]); L(mu.outputs[0], ramp.inputs[0]); L(ramp.outputs[0], b.inputs['Base Color'])
    return m

def add_flash(m, color):
    """Edge (facing-masked) emission + faint body emission. Returns (rim_socket, body_socket) to keyframe."""
    nt = m.node_tree; b = nt.nodes['Principled BSDF']; out = nt.nodes['Material Output']
    b.inputs['Emission Color'].default_value = (*color, 1); b.inputs['Emission Strength'].default_value = 0.0
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.0
    es = nt.nodes.new('ShaderNodeEmission'); es.inputs['Color'].default_value = (*color, 1)
    ml = nt.nodes.new('ShaderNodeMath'); ml.operation = 'MULTIPLY'; ml.inputs[1].default_value = 0.0
    ad = nt.nodes.new('ShaderNodeAddShader'); L = nt.links.new
    L(lw.outputs['Facing'], pw.inputs[0]); L(pw.outputs[0], ml.inputs[0]); L(ml.outputs[0], es.inputs['Strength'])
    L(b.outputs[0], ad.inputs[0]); L(es.outputs[0], ad.inputs[1]); L(ad.outputs[0], out.inputs['Surface'])
    return ml.inputs[1], b.inputs['Emission Strength']

def load_asset(dirpath):
    """import an asset folder's build.py/material.py as modules; returns (meta, build_mod, mat_mod)."""
    import importlib.util
    def imp(fn, nm):
        sp = importlib.util.spec_from_file_location(nm, os.path.join(dirpath, fn)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
    name = os.path.relpath(dirpath, os.path.dirname(os.path.abspath(__file__))).replace(os.sep, '_')
    return json.load(open(os.path.join(dirpath, 'meta.json'))), imp('build.py', f'asset_{name}_build'), imp('material.py', f'asset_{name}_mat')

def add_pins(meta):
    pi = meta['slots'].index('pin'); out = []
    for p in meta['pins']:
        y0, y1 = p['y_start'], WALL_Y + 0.01
        out.append(prim('cyl', pi, loc=(p['x'], (y0+y1)/2, p['z']), rot=(math.pi/2,0,0), scale=(p['radius'],p['radius'],y1-y0), verts=16))
    return out

def make_asset(meta, build_mod, variant, name, keep_slots=True):
    """Build one striker mesh object (geometry + pins joined), material slots ordered as meta['slots'] (left empty for the caller).
    keep_slots=True keeps each part's material index (needs the __slot placeholders, see _ensure_slots).
    keep_slots=False reproduces the v3 behaviour, where every part rendered in slot 0 (the body material) -
    used only by --look v3 so its renders stay reproducible."""
    parts = build_mod.build(__import__(__name__), None if variant == 'default' else variant)
    parts += add_pins(meta)
    o = join(parts, name); n = len(meta['slots'])
    for p in o.data.polygons: p.material_index = min(p.material_index, n-1) if keep_slots else 0
    while len(o.data.materials) > n: o.data.materials.pop(index=len(o.data.materials)-1)   # (materials.clear() would reset indices)
    return o

def set_slots(me, mats):
    """fill a make_asset mesh's slots (placeholders) with real materials, in meta['slots'] order"""
    for i, m in enumerate(mats):
        if i < len(me.materials): me.materials[i] = m
        else: me.materials.append(m)

def surface_points(o, spacing=0.006):
    """area-uniform surface samples of an object's evaluated mesh (local coords) -> numpy (N,3)."""
    import numpy as np
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); me = ev.to_mesh(); me.calc_loop_triangles()
    V = np.array([v.co[:] for v in me.vertices]); T = np.array([t.vertices[:] for t in me.loop_triangles])
    a, b, c = V[T[:,0]], V[T[:,1]], V[T[:,2]]; area = 0.5*np.linalg.norm(np.cross(b-a, c-a), axis=1)
    rng = np.random.default_rng(0); n = np.maximum(1, np.ceil(area/spacing**2).astype(int))
    idx = np.repeat(np.arange(len(T)), n); u = rng.random(len(idx)); v = rng.random(len(idx)); s = u+v > 1; u[s] = 1-u[s]; v[s] = 1-v[s]
    P = a[idx] + u[:,None]*(b[idx]-a[idx]) + v[:,None]*(c[idx]-a[idx])
    ev.to_mesh_clear(); return np.vstack([P, V]).astype(np.float32)
