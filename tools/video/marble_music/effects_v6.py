"""Phase 3 batch-1 effects for --look v6 (Blender 4.2 and 5.x headless).

Applied on top of the v5 scene: per-section backdrop colour, compositor bloom,
background snow, and hit sparks. Does not change striker geometry, so v5
keep-out / pair checks still apply.
"""
from __future__ import annotations

import math
import random
import sys
import os

import bpy
from mathutils import Vector

from blender_compat import iter_object_fcurves


# Dark, muted wall colours (linear RGB) — loud enough to read as a section
# change, dark enough that the marble and strikers stay in front.
THEME = {
    'rosewood': (0.28, 0.13, 0.11),  # castanets: lacquered mahogany
    'ivory':    (0.27, 0.25, 0.22),  # piano: warm greige
    'alu':      (0.13, 0.20, 0.32),  # vibraphone: cool steel blue
    'brass':    (0.30, 0.19, 0.08),  # tubular bells: amber
    'marimba':  (0.26, 0.13, 0.07),  # marimba: honduras rosewood dusk
    'kalimba':  (0.12, 0.22, 0.24),  # kalimba: teal steel
    'silver':   (0.17, 0.22, 0.27),  # flute: cool silver-grey
    'rainbow':  (0.28, 0.14, 0.13),  # xylophone: muted festive rose
    'ceramic':  (0.30, 0.15, 0.09),  # ocarina: terracotta
    'steel':    (0.14, 0.17, 0.30),  # glockenspiel: icy blue (against the red case)
    'chrome':   (0.22, 0.21, 0.12),  # steel drums: warm olive-gold
    'spruce':   (0.29, 0.15, 0.07),  # guitar: sunburst amber
}
THEME_FALLBACK = (0.22, 0.22, 0.23)
TRANSITION_S = 0.5  # seconds


def _sections(keys):
    out = []
    for k in keys:
        if not out or out[-1]['track'] != k['track']:
            out.append({'track': k['track'], 't0': k['t'], 't1': k['t'], 'kind': None, 'keys': [k]})
        else:
            out[-1]['t1'] = k['t']
            out[-1]['keys'].append(k)
    return out


def _set_socket_color(sock, rgb, frame=None):
    sock.default_value = (rgb[0], rgb[1], rgb[2], 1.0)
    if frame is not None:
        sock.keyframe_insert('default_value', frame=frame)


def _dim(rgb, s=0.55):
    return (rgb[0] * s, rgb[1] * s, rgb[2] * s)


def apply_backdrop(wall_bsdf, world_bg, P, fps, look_for):
    """Keyframe the wall (and a matching dim world tint) across the 12 sections."""
    secs = _sections(P['keys'])
    for s in secs:
        s['kind'] = look_for(s['track'], s['keys'][0].get('drum', False))
        s['color'] = THEME.get(s['kind'], THEME_FALLBACK)
    wall_c = wall_bsdf.inputs['Base Color']
    world_c = world_bg.inputs[0]
    # hold the first section from frame 0
    _set_socket_color(wall_c, secs[0]['color'], 0)
    _set_socket_color(world_c, _dim(secs[0]['color']), 0)
    for i in range(1, len(secs)):
        t1 = secs[i]['t0']
        f0 = max(0, int(round((t1 - TRANSITION_S) * fps)))
        f1 = max(f0 + 1, int(round(t1 * fps)))
        _set_socket_color(wall_c, secs[i - 1]['color'], f0)
        _set_socket_color(world_c, _dim(secs[i - 1]['color']), f0)
        _set_socket_color(wall_c, secs[i]['color'], f1)
        _set_socket_color(world_c, _dim(secs[i]['color']), f1)
    # hold the last colour through the end of the song
    end_f = len(P['marble']) - 1
    _set_socket_color(wall_c, secs[-1]['color'], end_f)
    _set_socket_color(world_c, _dim(secs[-1]['color']), end_f)
    print('v6 backdrop: %d sections, %.2fs transitions' % (len(secs), TRANSITION_S), flush=True)


def _set_node_in(node, names, val):
    """Set a compositor input or legacy attribute (Blender 4.2 props / 5.x sockets)."""
    for n in names:
        sock = None
        if hasattr(node.inputs, 'get'):
            sock = node.inputs.get(n)
        if sock is None:
            for s in node.inputs:
                if s.name == n or getattr(s, 'identifier', '') == n:
                    sock = s
                    break
        if sock is not None:
            try:
                sock.default_value = val
                return True
            except Exception:
                pass
        attr = n.lower().replace(' ', '_')
        if hasattr(node, attr):
            try:
                setattr(node, attr, val)
                return True
            except Exception:
                pass
    return False


def apply_bloom(sc, threshold=1.05, size=6, mix=0.0, strength=0.65):
    """Insert a Glare node between Render Layers and Composite.

    Uses BLOOM when the enum exists, otherwise FOG_GLOW. Properties are set both
    as 4.2 attributes and as 5.x sockets so the same script runs headless on both.
    """
    sc.use_nodes = True
    if hasattr(sc.render, 'use_compositing'):
        sc.render.use_compositing = True
    if hasattr(sc.render, 'compositor'):
        for v in ('CPU', 'ALWAYS', 'GPU', 'ENABLED'):
            try:
                sc.render.compositor = v
                break
            except Exception:
                continue
    nt = sc.node_tree
    rl = next((n for n in nt.nodes if n.type == 'R_LAYERS'), None)
    comp = next((n for n in nt.nodes if n.type == 'COMPOSITE'), None)
    if rl is None:
        rl = nt.nodes.new('CompositorNodeRLayers')
    if comp is None:
        comp = nt.nodes.new('CompositorNodeComposite')
    # drop any existing Image links into Composite so we can insert Glare
    for link in list(nt.links):
        if link.to_node == comp and link.to_socket == comp.inputs[0]:
            nt.links.remove(link)
    glare = nt.nodes.new('CompositorNodeGlare')
    glare.location = (rl.location.x + 200, rl.location.y)
    comp.location = (glare.location.x + 200, glare.location.y)
    typ = None
    for t in ('BLOOM', 'FOG_GLOW'):
        try:
            glare.glare_type = t
            typ = t
            break
        except Exception:
            continue
    if hasattr(glare, 'quality'):
        try:
            glare.quality = 'MEDIUM'
        except Exception:
            pass
    _set_node_in(glare, ('Threshold', 'threshold'), threshold)
    # 4.2 size is an int 1-9; 5.x Fog Glow / Bloom size may be a float
    size_set = False
    if typ == 'BLOOM' or typ is None:
        size_set = _set_node_in(glare, ('Size', 'size'), size) or _set_node_in(glare, ('Size', 'size'), int(size))
    else:
        size_set = _set_node_in(glare, ('Size', 'Fog Glow Size', 'size'), size)
        if not size_set and hasattr(glare, 'size'):
            try:
                glare.size = int(max(1, min(9, size)))
                size_set = True
            except Exception:
                pass
    if hasattr(glare, 'size') and not size_set:
        try:
            glare.size = int(max(1, min(9, size)))
        except Exception:
            pass
    _set_node_in(glare, ('Mix', 'mix'), mix)
    _set_node_in(glare, ('Strength', 'strength', 'Glow Strength'), strength)
    img_out = rl.outputs.get('Image') if hasattr(rl.outputs, 'get') else rl.outputs[0]
    img_in = glare.inputs.get('Image') if hasattr(glare.inputs, 'get') else glare.inputs[0]
    img_gout = glare.outputs.get('Image') if hasattr(glare.outputs, 'get') else glare.outputs[0]
    nt.links.new(img_out, img_in)
    nt.links.new(img_gout, comp.inputs[0])
    print('v6 bloom: type=%s threshold=%.2f size=%s' % (typ, threshold, size), flush=True)


def apply_marble_glow(mm, mbsdf):
    """A faint green rim emission so the marble itself blooms, without washing the glass."""
    nt = mm.node_tree
    out = nt.nodes['Material Output']
    # keep the existing surface (Principled) and add a LayerWeight-facing emission
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.35
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (0.20, 1.0, 0.45, 1)
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = 0.8
    add = nt.nodes.new('ShaderNodeAddShader')
    nt.links.new(lw.outputs['Facing'], mul.inputs[0])
    nt.links.new(mul.outputs[0], em.inputs['Strength'])
    # current surface link may already go Principled -> Output; re-hook via Add
    nt.links.new(mbsdf.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    # replace Surface input
    for link in list(nt.links):
        if link.to_node == out and link.to_socket == out.inputs['Surface']:
            nt.links.remove(link)
    nt.links.new(add.outputs[0], out.inputs['Surface'])


def _linear_cycles(obj, data_path, index, f0, v0, f1, v1):
    """Two-key LINEAR location/value curve with a CYCLES modifier (falling snow wrap)."""
    if data_path == 'location':
        obj.location[index] = v0
        obj.keyframe_insert('location', index=index, frame=f0)
        obj.location[index] = v1
        obj.keyframe_insert('location', index=index, frame=f1)
    else:
        return
    for fc in iter_object_fcurves(obj):
        if fc.data_path == data_path and fc.array_index == index:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'
            # avoid stacking modifiers if this is ever called twice
            if not any(m.type == 'CYCLES' for m in fc.modifiers):
                fc.modifiers.new(type='CYCLES')


def apply_snow(sc, rig, cam, n_back=70, n_fore=40):
    """Gentle falling flakes. Background layer sits just in front of the wall
    (y≈0.22–0.28, behind the marble so it never occludes the path). A sparser
    mid-foreground layer is kept to the left/right gutters and the very top/bottom
    of the 9:16 frame so it does not cross the marble.
    """
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=1, location=(0, 0, -40))
    ico = bpy.context.object
    snow_me = ico.data
    snow_me.name = 'snowflake'
    bpy.data.objects.remove(ico, do_unlink=True)

    mat, _ = _snow_mat()
    snow_me.materials.append(mat)
    rng = random.Random(126)

    # camera NDC in rig space (cam is parented to the rig, rig has no rotation)
    inv = cam.matrix_basis.inverted()
    tanv = (36.0 / 2.0) / 40.0
    tanh = tanv * 9.0 / 16.0

    def ndc(rloc):
        c = inv @ Vector(rloc)
        if c.z >= -0.05:
            return None
        u = c.x / (-c.z) / tanh
        v = c.y / (-c.z) / tanv
        return u, v

    def make_flake(name, loc, scale, speed, z_top, z_bot, x_amp=0.0, x_period=0):
        o = bpy.data.objects.new(name, snow_me)
        sc.collection.objects.link(o)
        o.parent = rig
        o.location = loc
        o.scale = (scale, scale, scale)
        o.visible_shadow = False
        if hasattr(o, 'visible_volume_scatter'):
            o.visible_volume_scatter = False
        period = max(8, int(round(abs(z_top - z_bot) / max(speed, 1e-4) * sc.render.fps)))
        # fall from current z down by (z_top-z_bot); CYCLES wraps
        _linear_cycles(o, 'location', 2, 0, loc[2], period, loc[2] - abs(z_top - z_bot))
        if x_amp and x_period:
            _linear_cycles(o, 'location', 0, 0, loc[0] - x_amp, x_period, loc[0] + x_amp)
        return o

    # --- background: just in front of the wall, behind the marble (y> R) ---
    n_ok = 0
    tries = 0
    while n_ok < n_back and tries < n_back * 20:
        tries += 1
        x = rng.uniform(-2.4, 2.8)
        y = rng.uniform(0.225, 0.285)  # behind marble (R=0.15), in front of wall (0.30)
        z = rng.uniform(-4.0, 2.2)
        uv = ndc((x, y, z))
        if uv is None or abs(uv[0]) > 1.25 or abs(uv[1]) > 1.25:
            continue
        scale = rng.uniform(0.007, 0.014)
        speed = rng.uniform(0.22, 0.48)  # units / second
        x_amp = rng.uniform(0.02, 0.08)
        x_per = rng.randint(40, 90)
        make_flake('snow_b%02d' % n_ok, (x, y, z), scale, speed, 2.2, -4.0, x_amp, x_per)
        n_ok += 1

    # --- mid-foreground gutter / top / bottom layer (never over the marble) ---
    n_f = 0
    tries = 0
    while n_f < n_fore and tries < n_fore * 40:
        tries += 1
        y = rng.uniform(-4.0, -0.8)
        x = rng.uniform(-2.2, 2.6)
        z = rng.uniform(-3.6, 2.0)
        uv = ndc((x, y, z))
        if uv is None:
            continue
        u, v = uv
        if abs(u) > 1.15 or abs(v) > 1.15:
            continue
        # keep-out: central corridor where the marble travels (upper-middle)
        in_corridor = (abs(u) < 0.72 and -0.55 < v < 0.60)
        if in_corridor:
            continue
        scale = rng.uniform(0.010, 0.020)
        speed = rng.uniform(0.28, 0.55)
        x_amp = rng.uniform(0.03, 0.10)
        x_per = rng.randint(35, 80)
        make_flake('snow_f%02d' % n_f, (x, y, z), scale, speed, 2.0, -3.6, x_amp, x_per)
        n_f += 1

    print('v6 snow: background %d, foreground-gutter %d' % (n_ok, n_f), flush=True)


def _snow_mat():
    m = bpy.data.materials.new('snow')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.86, 0.90, 0.95, 1)
    b.inputs['Roughness'].default_value = 0.72
    b.inputs['Emission Color'].default_value = (0.80, 0.88, 1.0, 1)
    b.inputs['Emission Strength'].default_value = 0.18
    return m, b


def _shard_mesh(sc):
    bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=1.0, radius2=0.0, depth=4.0, location=(0, 0, -50))
    tmp = bpy.context.object
    me = tmp.data
    me.name = 'spark_shard'
    bpy.data.objects.remove(tmp, do_unlink=True)
    return me


def apply_sparks(sc, P, fps, R, look_for, FLASH, pool=12, n_shards=5):
    """Short-lived emissive shards at each marble impact, timed to the hit frame.

    A pool of `pool` bursts (each `n_shards` cones) is reused; min hit spacing is
    well above the 7-frame lifetime, so slots never overlap.
    """
    me = _shard_mesh(sc)
    if len(me.materials) == 0:
        ph = bpy.data.materials.new('spark_placeholder')
        me.materials.append(ph)
    bursts = []
    for b in range(pool):
        shards = []
        for s in range(n_shards):
            mat = bpy.data.materials.new('spark_%d_%d' % (b, s))
            mat.use_nodes = True
            principled = mat.node_tree.nodes['Principled BSDF']
            principled.inputs['Base Color'].default_value = (1, 1, 1, 1)
            principled.inputs['Roughness'].default_value = 0.25
            # emission is what bloom picks up; start off
            col = principled.inputs['Emission Color']
            em = principled.inputs['Emission Strength']
            em.default_value = 0.0
            o = bpy.data.objects.new('spark_%d_%d' % (b, s), me)
            sc.collection.objects.link(o)
            o.scale = (0.0, 0.0, 0.0)
            o.visible_shadow = False
            if len(o.material_slots) == 0:
                o.data.materials.append(mat)
            o.material_slots[0].link = 'OBJECT'
            o.material_slots[0].material = mat
            o.hide_render = True
            shards.append((o, mat, col, em))
        bursts.append(shards)

    n_keys = len(P['keys'])
    for i, k in enumerate(P['keys']):
        shards = bursts[i % pool]
        fh = k['t'] * fps
        fi = max(0, min(len(P['marble']) - 1, int(round(fh))))
        mx, mz = P['marble'][fi]
        nx, nz = k['nx'], k['nz']
        # Contact is at the marble/striker meeting point in XZ. Spawn just in front
        # of the marble (y < -R) so the burst is not hidden inside the glass.
        origin = Vector((mx - nx * R * 0.85, -0.17, mz - nz * R * 0.85))
        kind = look_for(k['track'], k.get('drum', False))
        rgb = FLASH.get(kind, (1.0, 0.85, 0.5))
        # stable per-hit spray directions
        rng = random.Random(10007 + k['i'] * 13)
        T = Vector((nz, 0, -nx))
        N = Vector((nx, 0, nz))
        Cam = Vector((0, -1, 0))
        for si, (o, mat, col, em) in enumerate(shards):
            ang = (si / float(n_shards)) * 2.0 * math.pi + rng.uniform(-0.25, 0.25)
            spread = N * 0.15 + Cam * 0.75 + T * math.cos(ang) * 0.85 + N.cross(T) * math.sin(ang) * 0.5
            if spread.length < 1e-6:
                spread = Cam
            spread = spread.normalized()
            dist = rng.uniform(0.12, 0.22)
            end = origin + spread * dist
            # aim the cone along the flight direction (cone points +Z locally)
            quat = Vector((0, 0, 1)).rotation_difference(spread)
            o.rotation_euler = quat.to_euler()
            # hide / show (CONSTANT so the boolean does not interpolate)
            for f, hid in ((fh - 2, True), (fh - 0.5, False), (fh + 7, True)):
                o.hide_render = hid
                o.keyframe_insert('hide_render', frame=f)
            # location
            for f, loc in ((fh - 0.5, origin), (fh, origin), (fh + 6, end)):
                o.location = loc
                o.keyframe_insert('location', frame=f)
            # scale: thin needles, fade out
            sx, sy, sz = 0.008, 0.008, 0.016
            for f, s in ((fh - 0.5, 0.0), (fh, 1.0), (fh + 3, 0.7), (fh + 7, 0.0)):
                o.scale = (sx * s, sy * s, sz * s)
                o.keyframe_insert('scale', frame=f)
            col.default_value = (rgb[0], rgb[1], rgb[2], 1)
            col.keyframe_insert('default_value', frame=fh)
            for f, v in ((fh - 0.5, 0.0), (fh, 14.0), (fh + 3, 4.0), (fh + 7, 0.0)):
                em.default_value = v
                em.keyframe_insert('default_value', frame=f)

    # CONSTANT interpolation on hide_render (and on scale/location jumps at emit time)
    for shards in bursts:
        for o, mat, col, em in shards:
            for fc in iter_object_fcurves(o):
                if fc.data_path == 'hide_render':
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'CONSTANT'
                elif fc.data_path in ('location', 'scale', 'rotation_euler'):
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'LINEAR'
    print('v6 sparks: %d hits, pool %d x %d shards' % (n_keys, pool, n_shards), flush=True)


def apply_v6(sc, P, fps, R, wd, bg, wall, wall_bsdf, mb, mm, mbsdf, rig, cam, look_for, FLASH):
    apply_backdrop(wall_bsdf, bg, P, fps, look_for)
    apply_marble_glow(mm, mbsdf)
    apply_bloom(sc)
    apply_snow(sc, rig, cam)
    apply_sparks(sc, P, fps, R, look_for, FLASH)
    print('v6 effects applied', flush=True)


def apply_v7(sc, P, fps, R, wd, bg, wall, wall_bsdf, mb, mm, mbsdf, rig, cam, look_for, FLASH):
    """v7: same per-section backdrop and marble glow as v6, but no snow or sparks,
    and a higher bloom threshold so chrome/silver strikers (flute, steel drums) do not blow out.
    """
    apply_backdrop(wall_bsdf, bg, P, fps, look_for)
    apply_marble_glow(mm, mbsdf)
    apply_bloom(sc, threshold=1.30, size=6, mix=0.0, strength=0.50)
    print('v7 effects applied (backdrop + tamer bloom; no snow/sparks)', flush=True)
