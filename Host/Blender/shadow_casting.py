"""Which objects throw which shadows, as their renderers state it.

A renderer states how it draws into shadow maps (Unity's ShadowCastingMode), and a
streamed renderer also whether that shadow falls in the directional light's
cascades. Shadows-only is object visibility. The cascades have no per-object
switch here: an object blocks a light or it does not, per light, and that is
light linking. The objects that cast for local lights only are gathered in one
collection, each excluded, and that collection is the blocker set of whichever
light the shading stacks pick as their main light -- an exclude-only set leaves
every other object blocking it.
"""

from __future__ import annotations

import bpy

MAIN_LIGHT_EXCLUSIONS = "Ruri Main Light Shadow Exclusions"


def shadow_only(obj):
    """Seen by shadow rays and nothing else: no camera, reflection, refraction,
    medium or light probe."""
    obj.visible_camera = False
    obj.visible_diffuse = False
    obj.visible_glossy = False
    obj.visible_transmission = False
    obj.visible_volume_scatter = False
    obj.hide_probe_volume = True
    obj.hide_probe_sphere = True
    obj.hide_probe_plane = True


def exclude_from_main_light(obj):
    """Keep ``obj`` from blocking the main light while it blocks every other one."""
    collection = bpy.data.collections.get(MAIN_LIGHT_EXCLUSIONS)
    if collection is None:
        collection = bpy.data.collections.new(MAIN_LIGHT_EXCLUSIONS)
    if collection.objects.get(obj.name) is obj:
        return
    collection.objects.link(obj)
    # A link appends: the entry just made is the last one, and it starts included --
    # an include in a blocker set would make it one of the ONLY blockers.
    collection.collection_objects[len(collection.collection_objects) - 1].light_linking.link_state = "EXCLUDE"


def bind_main_light(main):
    """Make the exclusion set the blocker set of ``main`` and of no other light."""
    collection = bpy.data.collections.get(MAIN_LIGHT_EXCLUSIONS)
    if collection is None:
        return
    for obj in bpy.data.objects:
        if obj.type != "LIGHT":
            continue
        linking = obj.light_linking
        if obj == main:
            if linking.blocker_collection != collection:
                linking.blocker_collection = collection
        elif linking.blocker_collection == collection:
            linking.blocker_collection = None
