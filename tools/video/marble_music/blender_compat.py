"""Blender 4.x / 5.x compatibility helpers for marble_music scripts.

Blender 5.0+ removed ``Action.fcurves`` in favour of slotted channelbags.
On macOS with Blender 5.3 this shows up as::

    AttributeError: 'Action' object has no attribute 'fcurves'

before any frame is rendered. Prefer these helpers over touching ``action.fcurves``
directly so the same scripts keep working on 4.2 LTS and 5.x.
"""
from __future__ import annotations

try:
    from bpy_extras import anim_utils
except ImportError:  # very old Blender
    anim_utils = None


def iter_action_fcurves(action, action_slot=None):
    """Yield FCurves for an Action on Blender 4.x or 5.x."""
    if action is None:
        return
    if anim_utils is not None and action_slot is not None:
        bag = anim_utils.action_get_channelbag_for_slot(action, action_slot)
        if bag is not None and getattr(bag, 'fcurves', None):
            yield from bag.fcurves
            return
    fcurves = getattr(action, 'fcurves', None)
    if fcurves:
        yield from fcurves


def iter_object_fcurves(obj):
    """Yield FCurves attached to an object (handles Blender 5 action slots)."""
    ad = getattr(obj, 'animation_data', None)
    if not ad or not ad.action:
        return
    yield from iter_action_fcurves(ad.action, getattr(ad, 'action_slot', None))


def set_path_keyframe_interpolation(objects=None, long_path_threshold=40):
    """Set location/rotation paths to LINEAR when dense; otherwise BEZIER.

    ``objects`` defaults to ``bpy.data.objects``.
    """
    import bpy

    if objects is None:
        objects = bpy.data.objects
    for obj in objects:
        for fc in iter_object_fcurves(obj):
            dense = (
                fc.data_path in ('location', 'rotation_euler')
                and len(fc.keyframe_points) > long_path_threshold
            )
            interp = 'LINEAR' if dense else 'BEZIER'
            for kp in fc.keyframe_points:
                kp.interpolation = interp
