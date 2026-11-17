"""Build the guide mesh inside Blender. Imported only when a plan has guide_rail.

Materials match the hscroll satin-brass divider and a slightly brighter brass
channel from the same jewelbox metal family. No video is started here.
"""

import bpy


def build(plan, mat):
    rail = plan.get("guide_rail")
    if not rail:
        return
    channel_mat, _ = mat("guide_channel", (0.78, 0.62, 0.34), rough=0.28, metal=1.0)
    bracket_mat, _ = mat("guide_bracket", (0.62, 0.50, 0.30), rough=0.35, metal=1.0)
    mesh = bpy.data.meshes.new("guide_channel")
    mesh.from_pydata(rail["verts"], [], rail["faces"])
    mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new("guide_channel", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(channel_mat)
    # Brackets are the last faces; giving the whole mesh one brass and a second
    # slot lets the feet read as the same satin hardware as the family dividers.
    obj.data.materials.append(bracket_mat)
    brace = rail.get("bracket_face_start")
    if brace is not None:
        for poly in mesh.polygons:
            if poly.index >= brace:
                poly.material_index = 1
