"""Ending props for ending.py plans (built by scene.py when P['ending'] is set).
FINISH pad: black-lacquer podium, chequered-flag top inlay, gold rims, gold star medallion on the front; held off the wall by
a brass cantilever bracket (bolted wall plate, arm under the pad, two diagonal struts). On contact it dips, flashes gold and
the star stays lit (= finished). Optional P['ending']['subscribe']: the resting marble lifts, glows and bursts (sparks +
flash) into extruded 3D gold text facing the camera."""
import bpy, math, os, random
from mathutils import Vector

FONT_CANDIDATES = ['/usr/share/fonts/truetype/sand-box/google/Poppins/Poppins-ExtraBold.ttf',
                   '/usr/share/fonts/truetype/sand-box/google/Poppins/Poppins-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']

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

def _rod(p1, p2, r, m, parent=None):
    p1, p2 = Vector(p1), Vector(p2); d = p2 - p1
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=32, location=(p1 + p2) / 2)
    o = bpy.context.object; o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); o.data.materials.append(m)
    for poly in o.data.polygons: poly.use_smooth = True
    return o

def _key(sock, kv):
    for f, v in kv: sock.default_value = v; sock.keyframe_insert('default_value', frame=f)

def build(P, mat, fps):
    E = P['ending']; p = E['pad']; px, zt, r, h = p['x'], p['z_top'], p['r'], max(p['h'], 0.22); fc = E['frame_contact']
    yc = p.get('y', -0.08); sc = bpy.context.scene; wall_y = P['KD'] / 2 + 0.12
    gold, gb = mat('end_gold', (1.0, 0.70, 0.26), rough=0.16, metal=1.0); gb.inputs['Emission Color'].default_value = (1.0, 0.72, 0.3, 1)
    brass, _ = mat('end_brass', (0.62, 0.45, 0.22), rough=0.32, metal=1.0)
    lac, lb = mat('end_lacquer', (0.02, 0.02, 0.025), rough=0.25, coat=1.0); lb.inputs['Coat Roughness'].default_value = 0.03
    chk, cb = mat('end_check', (0.9, 0.9, 0.9), rough=0.3, coat=0.6)
    nt = chk.node_tree; ct = nt.nodes.new('ShaderNodeTexChecker'); tc = nt.nodes.new('ShaderNodeTexCoord')
    ct.inputs['Scale'].default_value = 7.0; ct.inputs['Color1'].default_value = (0.86, 0.84, 0.80, 1); ct.inputs['Color2'].default_value = (0.012, 0.012, 0.014, 1)
    nt.links.new(tc.outputs['Object'], ct.inputs['Vector']); nt.links.new(ct.outputs['Color'], cb.inputs['Base Color'])
    star_m, sb = mat('end_star', (1.0, 0.74, 0.28), rough=0.12, metal=1.0); sb.inputs['Emission Color'].default_value = (1.0, 0.78, 0.35, 1)
    root = bpy.data.objects.new('end_pad', None); sc.collection.objects.link(root); root.location = (px, yc, zt)
    def add(o, m=None):
        if m: o.data.materials.append(m)
        mw = o.matrix_world.copy(); o.parent = root; o.matrix_parent_inverse = root.matrix_world.inverted()
        for poly in o.data.polygons: poly.use_smooth = True
        return o
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=96, location=(px, yc, zt - h / 2)); body = add(bpy.context.object, lac)
    bv = body.modifiers.new('bev', 'BEVEL'); bv.width = 0.01; bv.segments = 2; bv.limit_method = 'ANGLE'
    bpy.ops.mesh.primitive_cylinder_add(radius=r * 0.84, depth=0.006, vertices=96, location=(px, yc, zt + 0.002)); add(bpy.context.object, chk)
    for zz, mr in ((zt, 0.024), (zt - h, 0.018)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=mr, major_segments=128, minor_segments=16, location=(px, yc, zz)); add(bpy.context.object, gold)
    bpy.ops.mesh.primitive_torus_add(major_radius=r * 0.86, minor_radius=0.008, major_segments=128, minor_segments=8, location=(px, yc, zt + 0.004)); add(bpy.context.object, gold)
    st = _star('end_star', px, yc - r - 0.004, zt - h / 2, h * 0.46, h * 0.19, 0.035); add(st, star_m)
    # ---- brass cantilever bracket: bolted wall plate + arm under the pad + two diagonal struts (the pad no longer touches the wall)
    # (the pad hides the wall ~0.55 m below itself from this camera, so the struts reach well down to a lower bolted plate)
    zb = zt - h; drop = 1.05; pw, ph = 0.36, 0.34; zp = zb - drop
    def plate(zc_, w_, h_):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(px, wall_y - 0.018, zc_)); pl = bpy.context.object; pl.scale = (w_, 0.036, h_)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); m_ = pl.modifiers.new('bev', 'BEVEL'); m_.width = 0.012; m_.segments = 3
        add(pl, brass)
        for bx in (-w_ / 2 + 0.055, w_ / 2 - 0.055):
            for bz in (zc_ + h_ / 2 - 0.055, zc_ - h_ / 2 + 0.055):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.024, segments=24, ring_count=12, location=(px + bx, wall_y - 0.036, bz)); bo = bpy.context.object; bo.scale = (1, 0.45, 1); add(bo, gold)
    plate(zb - 0.12, 0.30, 0.22); plate(zp, pw, ph)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(px, (wall_y + yc) / 2, zb - 0.035)); arm = bpy.context.object; arm.scale = (0.11, wall_y - yc, 0.07)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); m_ = arm.modifiers.new('bev', 'BEVEL'); m_.width = 0.01; m_.segments = 2
    add(arm, brass)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.05, vertices=64, location=(px, yc, zb - 0.025)); add(bpy.context.object, brass)
    ytip = yc - r * 0.55
    for sx in (-0.12, 0.12):
        add(_rod((px + sx, wall_y - 0.04, zp), (px + sx * 1.6, ytip, zb - 0.04), 0.034, brass))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=24, ring_count=12, location=(px + sx * 1.6, ytip, zb - 0.04)); add(bpy.context.object, gold)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, segments=24, ring_count=12, location=(px + sx, wall_y - 0.05, zp)); add(bpy.context.object, gold)
    add(_rod((px - 0.12 * 1.3, (wall_y + ytip) / 2 + 0.05, zp + drop * 0.62), (px + 0.12 * 1.3, (wall_y + ytip) / 2 + 0.05, zp + drop * 0.62), 0.02, brass))
    if E.get('look') == 'v4':                                       # v4: centre spine + gold collars where the struts meet the plate
        add(_rod((px, wall_y - 0.04, zp + ph / 2 - 0.02), (px, ytip + 0.12, zb - 0.06), 0.026, brass))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.036, segments=24, ring_count=12, location=(px, ytip + 0.12, zb - 0.06)); add(bpy.context.object, gold)
        for sx in (-0.12, 0.12):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.045, minor_radius=0.012, major_segments=32, minor_segments=8, location=(px + sx, wall_y - 0.06, zp))
            tr = bpy.context.object; tr.rotation_euler = (math.pi / 2, 0, 0); add(tr, gold)
    # contact: dip + gold flash (smaller dips on the hops), star stays lit afterwards
    kv = [(fc - 1, 0), (fc, 0), (fc + 1, -0.035), (fc + 3, -0.01), (fc + 7, 0)]
    for fh_ in E.get('frames_hop', []): kv += [(fh_, 0), (fh_ + 1, -0.01), (fh_ + 4, 0)]
    for f, dz in sorted(dict(kv).items()):
        root.location.z = zt + dz; root.keyframe_insert('location', index=2, frame=f)
    _key(sb.inputs['Emission Strength'], [(0, 0), (fc - 0.5, 0), (fc, 5.0), (fc + 6, 2.2), (fc + 24, 1.1)])
    _key(gb.inputs['Emission Strength'], [(0, 0), (fc - 0.5, 0), (fc, 1.6), (fc + 8, 0.35), (fc + 24, 0.12)])
    ld = bpy.data.lights.new('end_glow', 'POINT'); ld.color = (1.0, 0.75, 0.35); ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new('end_glow', ld); sc.collection.objects.link(lo); lo.location = (px, yc - r - 0.35, zt - h / 2)
    for f, v in [(0, 0), (fc - 0.5, 0), (fc, 40.0), (fc + 8, 12.0), (fc + 24, 6.0)]:
        ld.energy = v; ld.keyframe_insert('energy', frame=f)
    if E.get('subscribe'): (build_subscribe_fall if E['subscribe'].get('style') == 'fall' else build_subscribe_rise)(P, mat, fps)

def _cam_frame(P, f):
    """world camera position + basis at frame f (mirrors scene.py v2+ rig: offset (0.5,-5.3,1.0), aim (0,0,-0.9), lens 40, sensor 36 vertical)"""
    cx, cz = P['camera'][f]; rig = Vector((cx, 0, cz)); off = Vector((0.5, -5.3, 1.0)); aim = Vector((0, 0, -0.9))
    q = (aim - off).to_track_quat('-Z', 'Y'); sc = bpy.context.scene
    tv = 18.0 / 40.0; th = tv * sc.render.resolution_x / sc.render.resolution_y
    return rig + off, q, q @ Vector((1, 0, 0)), q @ Vector((0, 1, 0)), q @ Vector((0, 0, -1)), th, tv

def build_subscribe_fall(P, mat, fps):
    """the marble's last bounce: while it falls it turns gold and grows, bursts (flash + sparks) at frame_burst into two lines of
    extruded gold text that keep falling with the camera and land/settle on the empty wall (path precomputed by ending.py)."""
    S = P['ending']['subscribe']; f_r, fb, fl = S['frame_release'], S['frame_burst'], S['frame_land']; sc = bpy.context.scene
    nfr = len(P['marble']); cam, q, rt, up, fw, th, tv = _cam_frame(P, nfr - 1); full_w = S['full_w']
    path = {int(k): Vector(v) for k, v in S['path'].items()}
    tm, tb = mat('end_text', (0.62, 0.38, 0.06), rough=0.30, metal=1.0); tb.inputs['Emission Color'].default_value = (1.0, 0.66, 0.22, 1)
    font = next((bpy.data.fonts.load(f) for f in FONT_CANDIDATES if os.path.exists(f)), None)
    objs = []
    for body, wf in ((S['line1'], 0.74), (S['line2'], S['width_frac'])):
        cu = bpy.data.curves.new(f'txt_{len(objs)}', 'FONT'); cu.body = body; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        if font: cu.font = font
        cu.size = 1.0; cu.extrude = 0.07; cu.bevel_depth = 0.018; cu.bevel_resolution = 3; cu.resolution_u = 8
        o = bpy.data.objects.new(f'txt_{len(objs)}', cu); sc.collection.objects.link(o); o.data.materials.append(tm)
        bpy.context.view_layer.update(); s_ = wf * full_w / max(o.dimensions.x, 1e-6); cu.size = s_; cu.extrude = 0.07 * s_; cu.bevel_depth = 0.018 * s_
        bpy.context.view_layer.update(); objs.append((o, o.dimensions.y))
    (o1, h1), (o2, h2) = objs; gap = 0.35 * h2; offs = [up * ((h2 + gap) / 2), -up * ((h1 + gap) / 2)]
    blk = bpy.data.objects.new('txt_block', None); sc.collection.objects.link(blk); blk.rotation_euler = q.to_euler()
    for (o, _), d in zip(objs, offs):
        o.parent = blk; o.location = q.inverted() @ d                  # local offsets inside the camera-facing block
    for f in range(fb, nfr):
        blk.location = path.get(f, path[max(path)]); blk.keyframe_insert('location', frame=f)
    for k, (o, _) in enumerate(objs):                                  # grow out of the burst (line 2 a beat later)
        f1 = fb + 1 + 2 * k
        o.hide_render = True; o.keyframe_insert('hide_render', frame=0); o.hide_render = False; o.keyframe_insert('hide_render', frame=f1)
        for f, s_ in [(f1 - 1, 0.001), (f1, 0.08), (f1 + 6, 1.06), (f1 + 10, 0.98), (f1 + 14, 1.0)]:
            o.scale = (s_, s_, s_); o.keyframe_insert('scale', frame=f)
    _key(tb.inputs['Emission Strength'], [(0, 0), (fb, 3.0), (fb + 8, 0.6), (fl, 0.25), (fl + 3, 0.9), (fl + 16, 0.03)])   # small glint on landing
    # marble turns into solid glowing gold while it falls, grows a little, collapses into the burst
    mb = bpy.data.objects['marble']; mm = mb.active_material; nt = mm.node_tree; bs = nt.nodes['Principled BSDF']
    bs.inputs['Emission Color'].default_value = (1.0, 0.50, 0.08, 1); g0 = f_r + 1; g1 = min(fb - 1, f_r + 5)   # quick green->gold (a slow blend reads olive)
    _key(bs.inputs['Transmission Weight'], [(g0, 1.0), (g1, 0.0)]); _key(bs.inputs['Metallic'], [(g0, 0.0), (g1, 1.0)])
    _key(bs.inputs['Roughness'], [(g0, 0.02), (g1, 0.24)]); _key(bs.inputs['Emission Strength'], [(0, 0), (g0, 0.0), (g1, 0.5), (fb, 1.2)])
    bc = bs.inputs['Base Color']; bc.default_value = (0.05, 0.75, 0.35, 1); bc.keyframe_insert('default_value', frame=g0)
    bc.default_value = (0.80, 0.48, 0.09, 1); bc.keyframe_insert('default_value', frame=g1)
    vol = next((n for n in nt.nodes if n.type == 'VOLUME_ABSORPTION'), None)
    if vol: _key(vol.inputs['Density'], [(g0, 6.0), (g1, 0.0)])
    for f, s_ in [(g0, 1.0), (fb, 1.35), (fb + 2, 0.02)]:
        mb.scale = (s_, s_, s_); mb.keyframe_insert('scale', frame=f)
    mb.hide_render = False; mb.keyframe_insert('hide_render', frame=0); mb.hide_render = True; mb.keyframe_insert('hide_render', frame=fb + 3)
    Pb = path[fb]
    ld = bpy.data.lights.new('sub_flash', 'POINT'); ld.color = (1.0, 0.68, 0.28); ld.shadow_soft_size = 0.4
    lo = bpy.data.objects.new('sub_flash', ld); sc.collection.objects.link(lo); lo.location = Pb - fw * 0.4
    for f, v in [(0, 0), (fb - 3, 0), (fb, 260), (fb + 5, 70), (fb + 14, 0)]:
        ld.energy = v; ld.keyframe_insert('energy', frame=f)
    spm, spb = mat('end_spark', (1.0, 0.78, 0.35), rough=0.2, metal=1.0); spb.inputs['Emission Color'].default_value = (1.0, 0.72, 0.3, 1); spb.inputs['Emission Strength'].default_value = 6.0
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=2); tmpl = bpy.context.object; tmpl.data.materials.append(spm); smesh = tmpl.data
    bpy.data.objects.remove(tmpl, do_unlink=True); rnd = random.Random(5)
    for i in range(40):
        a_ = 2 * math.pi * i / 40 + rnd.uniform(-0.08, 0.08); spd = rnd.uniform(1.3, 2.8); life = rnd.randint(14, 22)
        dirv = (rt * math.cos(a_) + up * math.sin(a_) * 0.75 - fw * rnd.uniform(-0.2, 0.4)).normalized(); r0 = rnd.uniform(0.012, 0.024)
        o = bpy.data.objects.new(f'spark{i}', smesh); sc.collection.objects.link(o)
        o.hide_render = True; o.keyframe_insert('hide_render', frame=0); o.hide_render = False; o.keyframe_insert('hide_render', frame=fb + 1)
        o.hide_render = True; o.keyframe_insert('hide_render', frame=fb + 1 + life)
        for j in range(0, life + 1, 2):
            t = j / fps; dist = spd * (1 - math.exp(-t * 5)) / 5; base = path.get(fb + 1 + j, Pb).lerp(Pb, 0.55)   # drift down partly with the text
            o.location = base + dirv * dist * 1.2 + Vector((0, 0, -0.6 * t * t)); s_ = r0 * (1 - j / (life + 1)); o.scale = (s_, s_, s_)
            o.keyframe_insert('location', frame=fb + 1 + j); o.keyframe_insert('scale', frame=fb + 1 + j)

def build_subscribe_rise(P, mat, fps):
    """'rise' morph (look v2 = ending v2 unchanged; look v4 = gold glow + deeper text closer to the wall): the resting marble lifts, glows and bursts into text above the pad"""
    S = P['ending']['subscribe']; f_m0, ff = S['frame_morph'], S['frame_flash']; sc = bpy.context.scene
    cam, q, rt, up, fw, th, tv = _cam_frame(P, ff); wall_y = P['KD'] / 2 + 0.12
    def ray(sx, sy): return fw + (sx - 0.5) * 2 * th * rt + (0.5 - sy) * 2 * tv * up
    r0 = ray(*S['screen']); D = (wall_y - S.get('wall_gap', 0.3) - cam.y) / r0.y     # text plane sits wall_gap in front of the wall (in focus, casts a shadow)
    def pt(sx, sy, d=D): return cam + d * ray(sx, sy)
    Pc = pt(*S['screen']); full_w = 2 * D * th
    V4L = P['ending'].get('look') == 'v4'                                   # v4: deeper warmer gold text, gold (not pale) marble glow
    if V4L: tm, tb = mat('end_text', (0.62, 0.38, 0.06), rough=0.30, metal=1.0); tb.inputs['Emission Color'].default_value = (1.0, 0.66, 0.22, 1)
    else: tm, tb = mat('end_text', (0.95, 0.60, 0.16), rough=0.22, metal=1.0); tb.inputs['Emission Color'].default_value = (1.0, 0.75, 0.32, 1)
    font = next((bpy.data.fonts.load(f) for f in FONT_CANDIDATES if os.path.exists(f)), None)
    objs = []
    for body, wf in ((S['line1'], 0.74), (S['line2'], S['width_frac'])):
        cu = bpy.data.curves.new(f'txt_{len(objs)}', 'FONT'); cu.body = body; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        if font: cu.font = font
        cu.size = 1.0; cu.extrude = 0.06; cu.bevel_depth = 0.018; cu.bevel_resolution = 3; cu.resolution_u = 8
        o = bpy.data.objects.new(f'txt_{len(objs)}', cu); sc.collection.objects.link(o); o.data.materials.append(tm)
        bpy.context.view_layer.update(); s = wf * full_w / max(o.dimensions.x, 1e-6); cu.size = s; cu.extrude = 0.06 * s; cu.bevel_depth = 0.018 * s
        bpy.context.view_layer.update(); objs.append((o, o.dimensions.y))
    (o1, h1), (o2, h2) = objs; gap = 0.35 * h2
    for o, c in ((o1, Pc + up * ((h2 + gap) / 2)), (o2, Pc - up * ((h1 + gap) / 2))):
        o.location = c; o.rotation_euler = q.to_euler()
    for k, (o, _) in enumerate(objs):                                        # pop in with a little overshoot (line 2 a beat later)
        f1 = ff + 1 + 3 * k
        o.hide_render = True; o.keyframe_insert('hide_render', frame=0); o.hide_render = False; o.keyframe_insert('hide_render', frame=f1)
        for f, s in [(f1 - 1, 0.001), (f1, 0.05), (f1 + 5, 1.08), (f1 + 9, 0.98), (f1 + 12, 1.0)]:
            o.scale = (s, s, s); o.keyframe_insert('scale', frame=f)
    _key(tb.inputs['Emission Strength'], [(0, 0), (ff, 3.0 if V4L else 4.0), (ff + 8, 0.6 if V4L else 0.8), (ff + 22, 0.03 if V4L else 0.04)])
    # marble: lift from the pad to the text centre, grow + glow gold, then collapse into the flash
    mb = bpy.data.objects['marble']; mm = mb.active_material; bs = mm.node_tree.nodes['Principled BSDF']
    bs.inputs['Emission Color'].default_value = (1.0, 0.72, 0.3, 1)
    rest = Vector(P['ending']['rest']); rest = Vector((rest[0], rest[1], rest[2]))
    n = ff - f_m0
    for i in range(0, n + 1):
        u = i / n; s = u * u * (3 - 2 * u); p_ = rest.lerp(Pc, s) + Vector((0, 0, 0.35 * math.sin(math.pi * s)))
        mb.location = p_; mb.keyframe_insert('location', frame=f_m0 + i)
        sc_ = 1 + 0.6 * s; mb.scale = (sc_, sc_, sc_); mb.keyframe_insert('scale', frame=f_m0 + i)
    mb.scale = (1, 1, 1); mb.keyframe_insert('scale', frame=f_m0 - 1)
    for f, s in [(ff + 1, 1.0), (ff + 3, 0.02)]:
        mb.scale = (1.6 * s,) * 3; mb.keyframe_insert('scale', frame=f); mb.location = Pc; mb.keyframe_insert('location', frame=f)
    mb.hide_render = False; mb.keyframe_insert('hide_render', frame=0); mb.hide_render = True; mb.keyframe_insert('hide_render', frame=ff + 4)
    for f in range(ff + 4, len(P['marble'])):                               # park it (scene.py keyed rest positions there)
        mb.location = Pc; mb.keyframe_insert('location', frame=f)
    if V4L:                                                                # quick green -> solid gold as it lifts (a slow blend reads olive / pale)
        bs.inputs['Emission Color'].default_value = (1.0, 0.50, 0.08, 1); g0, g1 = f_m0, f_m0 + 5; nt_ = mm.node_tree
        _key(bs.inputs['Transmission Weight'], [(g0, 1.0), (g1, 0.0)]); _key(bs.inputs['Metallic'], [(g0, 0.0), (g1, 1.0)])
        _key(bs.inputs['Roughness'], [(g0, 0.02), (g1, 0.24)]); _key(bs.inputs['Emission Strength'], [(0, 0), (g0, 0), (g1, 0.4), (ff, 1.2)])
        bc = bs.inputs['Base Color']; bc.default_value = (0.05, 0.75, 0.35, 1); bc.keyframe_insert('default_value', frame=g0)
        bc.default_value = (0.80, 0.48, 0.09, 1); bc.keyframe_insert('default_value', frame=g1)
        vol = next((n_ for n_ in nt_.nodes if n_.type == 'VOLUME_ABSORPTION'), None)
        if vol: _key(vol.inputs['Density'], [(g0, 6.0), (g1, 0.0)])
    else: _key(bs.inputs['Emission Strength'], [(0, 0), (f_m0, 0), (f_m0 + n * 0.6, 1.5), (ff, 5.0)])
    # flash light + sparks bursting out in the camera plane
    ld = bpy.data.lights.new('sub_flash', 'POINT'); ld.color = (1.0, 0.68, 0.28) if V4L else (1.0, 0.8, 0.45); ld.shadow_soft_size = 0.4
    lo = bpy.data.objects.new('sub_flash', ld); sc.collection.objects.link(lo); lo.location = Pc - fw * 0.4
    for f, v in ([(0, 0), (f_m0, 0), (ff - 2, 40), (ff + 1, 300), (ff + 6, 80), (ff + 16, 0)] if V4L else [(0, 0), (f_m0, 0), (ff - 2, 60), (ff + 1, 450), (ff + 6, 120), (ff + 16, 25)]):
        ld.energy = v; ld.keyframe_insert('energy', frame=f)
    spm, spb = mat('end_spark', (1.0, 0.8, 0.4), rough=0.2, metal=1.0); spb.inputs['Emission Color'].default_value = (1.0, 0.82, 0.45, 1); spb.inputs['Emission Strength'].default_value = 8.0
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=2); tmpl = bpy.context.object; tmpl.data.materials.append(spm); smesh = tmpl.data
    bpy.data.objects.remove(tmpl, do_unlink=True); rnd = random.Random(5)
    for i in range(40):
        a_ = 2 * math.pi * i / 40 + rnd.uniform(-0.08, 0.08); spd = rnd.uniform(1.3, 2.8); life = rnd.randint(14, 22)
        dirv = (rt * math.cos(a_) + up * math.sin(a_) * 0.75 - fw * rnd.uniform(-0.2, 0.4)).normalized(); r0 = rnd.uniform(0.012, 0.024)
        o = bpy.data.objects.new(f'spark{i}', smesh); sc.collection.objects.link(o)
        o.hide_render = True; o.keyframe_insert('hide_render', frame=0); o.hide_render = False; o.keyframe_insert('hide_render', frame=ff + 1)
        o.hide_render = True; o.keyframe_insert('hide_render', frame=ff + 1 + life)
        for j in range(0, life + 1, 2):
            t = j / fps; dist = spd * (1 - math.exp(-t * 5)) / 5 * 1.0 + 0; z_ = -0.6 * t * t
            o.location = Pc + dirv * dist * 1.2 + Vector((0, 0, z_)); s = r0 * (1 - j / (life + 1)); o.scale = (s, s, s)
            o.keyframe_insert('location', frame=ff + 1 + j); o.keyframe_insert('scale', frame=ff + 1 + j)
