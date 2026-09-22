"""AzurPromilia -- everything the add-on has for this game and nothing else.

Two tabs, neither of which means anything for another title:

``Scene``      every scene the install carries, under the folder tree the game files it in, saying
               which of them ship a built scene file at all. (``scene``)
``Character``  the cast, read off the asset tree because this title ships no roster asset, and the
               parts each one is assembled from. (``roster``)

Three facts about this title decide the shape of both, and all three live upstream in
``Ruri.RipperHook.AzurPromilia`` rather than here:

* its bundles state ``0.0.0`` for their engine version, so a reader that believes them picks the
  wrong layout and reads noise -- the real version comes from the player's own settings file;
* a character has no single asset and no roster row: the character id is a LEVEL of the address
  tree, under a rig family, and each part is its own bundle carrying its own mesh and material;
* it rarely ships built scenes, so "which scenes exist" and "which scenes can be opened" are two
  different questions and a list that answers only one of them is misleading.

Declared as one GAME_MODULE row (see ``Game``), so the core panel reveals both tabs exactly while
the install in front of it IS this game, and never names it itself.
"""

from __future__ import annotations

import importlib

from .. import GameModule, GameSection, GameTab

#: The parts the two tabs are composed of, each with the capability its host must answer. Both tabs
#: of this game are the same act -- pick one of the things the asset tree names, and run the
#: browser's own import over what it resolved to. That needs nothing of the host the browser does
#: not already need, so both cross and neither declares a capability.
SECTIONS = (GameSection("roster"), GameSection("scene"))

_LOADED = []


def _register():
    _LOADED[:] = [importlib.import_module("." + one.id, __name__)
                  for one in SECTIONS if one.available]
    for module in _LOADED:
        module.register()


def _unregister():
    for module in reversed(_LOADED):
        module.unregister()
    _LOADED[:] = []


GAME_MODULE = GameModule(
    # The productName this game's player builds under, as its own app.info states it -- the same
    # string the upstream decoder declares, so the join is equality.
    game_name="AzurPromilia",
    label="Azur Promilia",
    sections=SECTIONS,
    tabs=(
        GameTab("scene", "Scene",
                "Every scene the install carries, and which of them ship a built scene file",
                ("scene", "draw")),
        GameTab("character", "Character",
                "The cast read off the asset tree, and the parts each one is assembled from",
                ("roster", "draw")),
    ),
    register=_register,
    unregister=_unregister,
)
