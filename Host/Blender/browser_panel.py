"""Blender's frame for the kernel's browser: the N-panel its description is rendered into, and the
selection shortcuts over it.

What the browser SAYS -- tabs, the install, the list, its import options, its animations -- is
described once (``Kernel.app.browser.draw``) and Painter's dock renders the same description. What
is Blender's is where the panel sits and which keys reach it.
"""

from __future__ import annotations

import bpy

from . import render
from ...Kernel.app import browser
from ...Kernel.app import layout as app_layout


class RURI_PT_browser(bpy.types.Panel):
    """The add-on's N-panel: a renderer for the kernel's browser description."""
    bl_idname = "RURI_PT_browser"
    bl_label = "RuriRipper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RuriRipper"

    def draw(self, context):
        render.draw(app_layout.describe(browser.draw, context), self.layout, context)


_KEYMAP_ITEMS = []


def register():
    browser.register()
    bpy.utils.register_class(RURI_PT_browser)


def unregister():
    bpy.utils.unregister_class(RURI_PT_browser)
    browser.unregister()


def register_keymaps():
    """Ctrl+A / Alt+A / Ctrl+I select all / none / invert while hovering the sidebar. In the "User
    Interface" keymap, the one active over any UI region; the command's own poll narrows it to the
    3D View sidebar with this category in front. Last of all at registration: an entry sets
    properties on the operator it names, which exists only once every command has its wrapper."""
    keyconfigs = getattr(bpy.context.window_manager, "keyconfigs", None)
    addon = keyconfigs.addon if keyconfigs else None
    if addon is None:
        return
    keymap = addon.keymaps.new(name="User Interface", space_type="EMPTY")
    for key, ctrl, alt, mode in (("A", True, False, "ALL"), ("A", False, True, "NONE"),
                                 ("I", True, False, "INVERT")):
        item = keymap.keymap_items.new(browser.CABMAP_SELECT_ALL.id, key, "PRESS",
                                       ctrl=ctrl, alt=alt)
        item.properties.mode = mode
        _KEYMAP_ITEMS.append((keymap, item))


def unregister_keymaps():
    for keymap, item in _KEYMAP_ITEMS:
        keymap.keymap_items.remove(item)
    _KEYMAP_ITEMS.clear()
