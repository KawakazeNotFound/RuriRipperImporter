"""Resolving WHICH rig a person means, and putting a stated thing into the
document.

The rig rules are this add-on's own and unchanged: an Armature modifier pointing
at a skeleton IS the binding, so picking a mesh is picking its rig. What changed
is underneath the import verbs -- a selection is stated once by the reader and
placed from that statement, so nothing here walks an asset database.
"""

from __future__ import annotations

import bpy

from ...Kernel import options as kernel_options
from . import rig_identity


#: The Unity tag a placed object carries, so a camera the game tagged can be
#: found again by what the game called it.
UNITY_TAG = "unity_tag"


DEFAULT_OPTIONS = dict(kernel_options.defaults(), **{
    "import_materials": True,
    "import_textures": True,
    "import_skeleton": True,
    "connect_alpha": True,
    # Which game this import is of (the upstream GameType member). The host knows it;
    # the importer only stamps what it is told, so nothing here names a game.
    "source_game": "",
    # The layered role table materials resolve their properties through
    # (Kernel.unity.texture_roles.RoleTable): the host loads the default
    # layer, the game module's own and the user's; None means the default alone.
    "texture_roles": None,
    # The product the role layers are filed under (see Kernel.app.browser._texture_role_game).
    "texture_roles_game": "",
})


def resolve_options(options):
    merged = dict(DEFAULT_OPTIONS)
    if options:
        merged.update(options)
    return merged


def maps_from_stamped_armature(arm_obj):
    """The maps dict build_action needs (nodes with .path/.local + path_to_bone),
    out of the Unity identity this rig's BONES carry -- what lets a standalone
    animation import target ANY armature this add-on ever built, in any session and
    under any names the user has since given its bones, without the character
    import's live state.

    None for a rig whose bones carry no identity: built by something else, or built
    before the identity moved onto them (rig_identity.adopt is the one action that
    fixes the second, and every caller says so by name)."""
    identity = rig_identity.of(arm_obj)
    return identity.maps() if identity is not None else None


# --- unified entry point ----------------------------------------------------


def armature_of(obj):
    """The armature ``obj`` stands for -- the ONE rule every flow in this add-on
    resolves a rig by, so "which skeleton did I pick" never means two things.

    An Armature MODIFIER pointing at a rig IS the binding, so selecting a mesh
    that carries one is exactly as good as selecting the skeleton itself: that
    is what the user is looking at and clicking on, and requiring the rig object
    to be picked out of the outliner instead is a demand with no meaning behind
    it. An armature PARENT is the structural fallback, for something hung off a
    bone with no modifier of its own.

    Deliberately not gated on obj.type == "MESH": a curve, a lattice or any
    other deformable carries the same modifier and means the same thing by it."""
    if obj is None:
        return None
    if obj.type == "ARMATURE":
        return obj
    for modifier in getattr(obj, "modifiers", ()):
        if modifier.type == "ARMATURE" and modifier.object is not None:
            return modifier.object
    parent = obj.parent
    return parent if parent is not None and parent.type == "ARMATURE" else None


def find_target_armature(context):
    """The armature a clip import should drive: the active object's rig (an
    armature, or the armature a selected mesh is bound to), else the single
    rig the selection resolves to, else the scene's single armature. None when
    nothing resolves or the choice is ambiguous -- the caller words the error."""
    active = armature_of(getattr(context, "active_object", None))
    if active is not None:
        return active
    selected = {armature_of(obj) for obj in getattr(context, "selected_objects", ())}
    selected.discard(None)
    if len(selected) == 1:
        return next(iter(selected))
    if selected:
        return None
    scene_armatures = [obj for obj in context.scene.objects if obj.type == "ARMATURE"]
    return scene_armatures[0] if len(scene_armatures) == 1 else None


def _place(context, database, token, options, label=""):
    """Put what ``token`` states into the document, once."""
    from . import materialise as materialiser
    from ...Kernel.app import loading

    if database is None or token is None:
        return loading.Built(warnings=["Nothing resolved to place."])
    statement = database.statement
    built = materialiser.materialise(context, statement, resolve_options(options))
    return loading.Built(armature=built.rig, missing=built.missing,
                         warnings=built.warnings, imported=built.imported)


def import_prefab_from_db(context, database, token, options=None):
    return _place(context, database, token, options)


def import_mesh_from_db(context, database, token, options=None):
    return _place(context, database, token, options)


def import_avatar_from_db(context, database, token, options=None, name=""):
    return _place(context, database, token, options, label=name)


def import_asset(context, filepath, options=None):
    """One asset picked off the disk rather than out of a loaded map."""
    from ...Kernel.app import loading

    database = loading.StatementDatabase([filepath])
    return _place(context, database, database.token, options)
