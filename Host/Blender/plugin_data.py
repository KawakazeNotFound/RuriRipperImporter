"""⛔ The plugin's own data is never written to a .blend.

A .blend holds content: meshes, textures, a level's data, each material's record (the ``ruri_uber_*``
properties a generated stack compiles its graph from), what a level and the post panel set on the scene,
the user's own settings. Everything the plugin makes FROM that content and its shipped products -- the
template node groups taken from a product, template materials, parameter tables, neutral placeholders, the
compositor tree and its images, vertex trees, the viewpoint, the fallback sun -- is born here as runtime
data, which Blender never writes. A file saved from any session holds none of it, so no build of the
plugin ever finds an older build's copy of its own data, and nothing the plugin makes can go stale in a
file.

When a file opens, and when the shading stacks load into a session that already holds one, the load pass
(:func:`material_builder.rebuild_plugin_data`) drops every piece of plugin data still in memory -- this
session's, or an older build's that a file saved before this rule -- then the generated stacks compile
every material from its record, and the derived-state stages rebuild the rest.

Before every save a guard makes anything still carrying the mark runtime and names it. That is a bug
report, not a fallback: a datablock carrying the mark was born outside :func:`born`.
"""

from __future__ import annotations

import bpy

#: The mark every datablock the plugin makes for itself carries, beside ``is_runtime_data``.
MARK = "ruri_plugin_data"

#: Every kind of datablock the plugin makes for itself.
KINDS = ("node_groups", "materials", "images", "textures", "objects", "lights", "meshes", "collections", "texts")


def born(block):
    """The birth of every datablock the plugin makes for itself: runtime data, never written to a .blend."""
    block.is_runtime_data = True
    block[MARK] = 1
    return block


def content(block):
    """A datablock the plugin made that becomes the document's own content -- a level image once a level
    fills it, a material instance copied off a template: written with the file from now on."""
    if MARK in block:
        del block[MARK]
    block.is_runtime_data = False
    return block


def purge():
    """Drop every datablock carrying the mark. The load pass rebuilds what is still wanted. Returns how many."""
    doomed = [block for kind in KINDS for block in getattr(bpy.data, kind)
              if block.library is None and block.get(MARK)]
    if doomed:
        bpy.data.batch_remove(doomed)
    return len(doomed)


@bpy.app.handlers.persistent
def _forbid_plugin_data_in_blend(*_args):
    """The guard at the only way out of a session: whatever carries the mark but is not runtime would be
    written -- it is made runtime before the write, and named."""
    leaked = []
    for kind in KINDS:
        for block in getattr(bpy.data, kind):
            if block.library is None and block.get(MARK) and not block.is_runtime_data:
                block.is_runtime_data = True
                leaked.append(block.name_full)
    if leaked:
        print("[plugin-data] !! {0} datablock(s) of the plugin's own were about to be written and are kept out "
              "of the file (born outside plugin_data.born): {1}".format(len(leaked), leaked[:20]), flush=True)


def register():
    if _forbid_plugin_data_in_blend not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(_forbid_plugin_data_in_blend)


def unregister():
    if _forbid_plugin_data_in_blend in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(_forbid_plugin_data_in_blend)
