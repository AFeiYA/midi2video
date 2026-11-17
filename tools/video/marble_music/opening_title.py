"""Title prelude on negative scene frames, before the original first hit."""
import math
import random


def frames_for_intro(fps):
    return round(fps * 1.6)


def add_gold_sweep(material, surface, right, center, half_width, start, end):
    """Animate a narrow strip of emission across the main title."""
    nodes, links = material.node_tree.nodes, material.node_tree.links
    position = nodes.new('ShaderNodeNewGeometry')
    project = nodes.new('ShaderNodeVectorMath')
    project.operation = 'DOT_PRODUCT'
    project.inputs[1].default_value = right
    links.new(position.outputs['Position'], project.inputs[0])

    distance = nodes.new('ShaderNodeMath')
    distance.operation = 'SUBTRACT'
    links.new(project.outputs['Value'], distance.inputs[0])
    for frame, side in ((start, -1), (end, 1)):
        distance.inputs[1].default_value = center.dot(right) + side * half_width * 0.90
        distance.inputs[1].keyframe_insert('default_value', frame=frame)

    absolute = nodes.new('ShaderNodeMath')
    absolute.operation = 'ABSOLUTE'
    links.new(distance.outputs[0], absolute.inputs[0])
    band = nodes.new('ShaderNodeMapRange')
    band.inputs['From Max'].default_value = half_width * 0.25
    band.inputs['To Min'].default_value = 0.60
    band.inputs['To Max'].default_value = 0.06
    links.new(absolute.outputs[0], band.inputs['Value'])
    links.new(band.outputs[0], surface.inputs['Emission Strength'])


def build(plan, scene, marble, material, font_path, title, subtitle):
    import bpy
    from mathutils import Vector

    fps = plan['fps']
    scene.frame_set(0)
    bpy.context.view_layer.update()
    camera = scene.camera
    origin = camera.matrix_world.translation.copy()
    orientation = camera.matrix_world.to_quaternion()
    right = orientation @ Vector((1, 0, 0))
    up = orientation @ Vector((0, 1, 0))
    forward = orientation @ Vector((0, 0, -1))
    contact = marble.location.copy()
    first_hit = plan['keys'][0]
    normal = Vector((first_hit['nx'], 0, first_hit['nz'])).normalized()
    next_x, next_z = plan['marble'][1]
    outgoing = (Vector((next_x, contact.y, next_z)) - contact) * fps
    incoming = outgoing.reflect(normal) if first_hit['t'] == 0 else outgoing
    gravity = Vector((0, 0, -plan['g']))

    def approach(frame):
        t = frame / fps
        return contact + incoming * t + 0.5 * gravity * t * t

    intro_frames = frames_for_intro(fps)
    start = -intro_frames
    reveal_end = start + round(fps * 0.20)
    gather = start + round(fps * 0.95)
    formation = -round(fps * 0.30)
    launch = approach(formation)
    # Place the tilted letter plane clear of the set wall near the top of the image.
    title_depth = (launch - origin).dot(forward) - 0.45
    half_height = title_depth * camera.data.sensor_height / (2 * camera.data.lens)
    half_width = half_height * scene.render.resolution_x / scene.render.resolution_y
    subtitle_center = origin + forward * title_depth + up * (half_height * 0.62)

    font = bpy.data.fonts.load(font_path) if font_path else None

    for index, (line, width, y) in enumerate((
        (title, 0.70, 0.80),
        (subtitle, 0.73, 0.62),
    )):
        if not line.strip():
            continue
        text = bpy.data.curves.new(f'intro_line_{index}', 'FONT')
        text.body = line
        text.align_x = 'CENTER'
        text.align_y = 'CENTER'
        if font:
            text.font = font
        obj = bpy.data.objects.new(text.name, text)
        scene.collection.objects.link(obj)
        gold, surface = material(f'intro_gold_{index}', (0.62, 0.38, 0.06), rough=0.30, metal=1.0)
        surface.inputs['Emission Color'].default_value = (1.0, 0.72, 0.3, 1.0)
        surface.inputs['Emission Strength'].default_value = 0.06
        obj.data.materials.append(gold)
        bpy.context.view_layer.update()
        text.size = min(half_height * (0.19 if index == 0 else 0.09), 2 * half_width * width / obj.dimensions.x)
        text.extrude = text.size * 0.045
        text.bevel_depth = text.size * 0.012
        text.bevel_resolution = 3
        obj.rotation_euler = orientation.to_euler()
        position = origin + forward * title_depth + up * (half_height * y)
        collapse_from = gather + (2 if index == 0 else 0)
        if index == 0:
            add_gold_sweep(gold, surface, right, position, half_width, start, reveal_end)
        initial_position = position - up * (half_height * 0.065 if index == 1 else 0.0)
        for frame, location, scale in (
            (start, initial_position, 1.0),
            (reveal_end, position, 1.0),
            (collapse_from, position, 1.0),
            (formation, launch, 0.015),
        ):
            obj.location = location
            obj.scale = (scale,) * 3
            obj.keyframe_insert('location', frame=frame)
            obj.keyframe_insert('scale', frame=frame)
        obj.hide_render = False
        obj.keyframe_insert('hide_render', frame=start)
        obj.hide_render = True
        obj.keyframe_insert('hide_render', frame=formation + 1)

    # Continue into the existing contact at scene frame 0, then let the original shot play.
    marble.hide_render = True
    marble.keyframe_insert('hide_render', frame=start)
    marble.hide_render = False
    marble.keyframe_insert('hide_render', frame=formation)
    marble.keyframe_insert('hide_render', frame=0)
    for frame in range(formation, 0):
        marble.location = approach(frame)
        marble.keyframe_insert('location', frame=frame)
    for frame, scale in ((formation, 0.32), (formation + 3, 1.0), (0, 1.0)):
        marble.scale = (scale,) * 3
        marble.keyframe_insert('scale', frame=frame)

    shimmer, shader = material('intro_shimmer', (1.0, 0.67, 0.18), rough=0.3)
    shader.inputs['Emission Color'].default_value = (1.0, 0.65, 0.15, 1.0)
    shader.inputs['Emission Strength'].default_value = 3.0
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1)
    template = bpy.context.object
    mesh = template.data
    mesh.materials.append(shimmer)
    bpy.data.objects.remove(template, do_unlink=True)
    rng = random.Random(24)
    for index in range(24):
        fleck = bpy.data.objects.new(f'intro_fleck_{index}', mesh)
        scene.collection.objects.link(fleck)
        spawn = subtitle_center + right * (rng.uniform(-0.68, 0.68) * half_width)
        spawn += up * (rng.uniform(-0.025, 0.025) * half_height)
        radius = rng.uniform(0.008, 0.020)
        for frame, location, scale in (
            (gather - 1, spawn, 0.0),
            (gather + 2, spawn.lerp(launch, 0.15), radius),
            (formation, launch, 0.0),
        ):
            fleck.location = location
            fleck.scale = (scale,) * 3
            fleck.keyframe_insert('location', frame=frame)
            fleck.keyframe_insert('scale', frame=frame)

    return intro_frames
