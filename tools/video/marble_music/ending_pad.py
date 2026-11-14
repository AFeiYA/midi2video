"""Gold FINISH pad for ending.py plans (built by scene.py when P['ending'] is set): a black-lacquer wall podium with a
chequered-flag top inlay, gold rims, a gold star medallion on the front (matches the finale striker) and a gold bracket.
On contact it dips, flashes gold and the star stays lit (= finished)."""
import bpy, math

def _star(name, cx, y, cz, ro, ri, d):
    v = []; n = 10
    for yy in (y, y + d):
        v.append((cx, yy, cz))
        for i in range(n):
            r = ro if i % 2 == 0 else ri; a = math.pi / 2 + i * math.pi / 5
            v.append((cx + r * math.cos(a), yy, cz + r * math.sin(a)))
    F = []; B = n + 1
    for i in range(n):
        j = (i + 1) % n
        F.append((0, 1 + j, 1 + i)); F.append((B, B + 1 + i, B + 1 + j)); F.append((1 + i, 1 + j, B + 1 + j, B + 1 + i))
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], F); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); return o

def build(P, mat, fps):
    E = P['ending']; p = E['pad']; px, zt, r, h = p['x'], p['z_top'], p['r'], max(p['h'], 0.22); fc = E['frame_contact']
    yc = -0.08; sc = bpy.context.scene
    gold, gb = mat('end_gold', (1.0, 0.70, 0.26), rough=0.16, metal=1.0)
    gb.inputs['Emission Color'].default_value = (1.0, 0.72, 0.3, 1)
    lac, lb = mat('end_lacquer', (0.02, 0.02, 0.025), rough=0.25, coat=1.0); lb.inputs['Coat Roughness'].default_value = 0.03
    chk, cb = mat('end_check', (0.9, 0.9, 0.9), rough=0.3, coat=0.6)
    nt = chk.node_tree; ct = nt.nodes.new('ShaderNodeTexChecker'); tc = nt.nodes.new('ShaderNodeTexCoord')
    ct.inputs['Scale'].default_value = 7.0; ct.inputs['Color1'].default_value = (0.86, 0.84, 0.80, 1); ct.inputs['Color2'].default_value = (0.012, 0.012, 0.014, 1)
    nt.links.new(tc.outputs['Object'], ct.inputs['Vector']); nt.links.new(ct.outputs['Color'], cb.inputs['Base Color'])
    star_m, sb = mat('end_star', (1.0, 0.74, 0.28), rough=0.12, metal=1.0); sb.inputs['Emission Color'].default_value = (1.0, 0.78, 0.35, 1)
    root = bpy.data.objects.new('end_pad', None); sc.collection.objects.link(root); root.location = (px, yc, zt)
    def add(o, m):
        o.data.materials.append(m); o.parent = root; o.location = (o.location.x - px, o.location.y - yc, o.location.z - zt)
        for poly in o.data.polygons: poly.use_smooth = True
        return o
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=96, location=(px, yc, zt - h / 2)); body = add(bpy.context.object, lac)
    bv = body.modifiers.new('bev', 'BEVEL'); bv.width = 0.01; bv.segments = 2; bv.limit_method = 'ANGLE'
    bpy.ops.mesh.primitive_cylinder_add(radius=r * 0.84, depth=0.006, vertices=96, location=(px, yc, zt + 0.002)); add(bpy.context.object, chk)
    for zz, mr in ((zt, 0.024), (zt - h, 0.018)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=mr, major_segments=128, minor_segments=16, location=(px, yc, zz)); add(bpy.context.object, gold)
    bpy.ops.mesh.primitive_torus_add(major_radius=r * 0.86, minor_radius=0.008, major_segments=128, minor_segments=8, location=(px, yc, zt + 0.004)); add(bpy.context.object, gold)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 0.18, radius2=r * 0.7, depth=0.22, vertices=64, location=(px, yc + 0.1, zt - h - 0.11)); add(bpy.context.object, gold)
    st = _star('end_star', px, yc - r - 0.004, zt - h / 2, h * 0.46, h * 0.19, 0.035); add(st, star_m)
    st.rotation_euler = (0, 0, 0)
    # contact: dip + gold flash, star stays lit afterwards
    for f, dz in [(fc - 1, 0), (fc, 0), (fc + 1, -0.035), (fc + 3, -0.01), (fc + 7, 0)]:
        root.location.z = zt + dz; root.keyframe_insert('location', index=2, frame=f)
    es = sb.inputs['Emission Strength']
    for f, v in [(0, 0), (fc - 0.5, 0), (fc, 5.0), (fc + 6, 2.2), (fc + 24, 1.1)]:
        es.default_value = v; es.keyframe_insert('default_value', frame=f)
    eg = gb.inputs['Emission Strength']
    for f, v in [(0, 0), (fc - 0.5, 0), (fc, 1.6), (fc + 8, 0.35), (fc + 24, 0.12)]:
        eg.default_value = v; eg.keyframe_insert('default_value', frame=f)
    ld = bpy.data.lights.new('end_glow', 'POINT'); ld.color = (1.0, 0.75, 0.35); ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new('end_glow', ld); sc.collection.objects.link(lo); lo.location = (px, yc - r - 0.35, zt - h / 2)
    for f, v in [(0, 0), (fc - 0.5, 0), (fc, 40.0), (fc + 8, 12.0), (fc + 24, 6.0)]:
        ld.energy = v; ld.keyframe_insert('energy', frame=f)
