"""This game's answer to "bring the model's own secondary motion across".

Two ways in, one implementation, and neither of them is here: the import options
carry it as a switch and the asset browser as a button, both drawn by the core panel
off the capability the option declares. What IS here is the READING -- the core
never learns that these settings exist, only that this game answered.

Writing them onto a rig is the host's (``Host.write_secondary_motion``), because
which solver holds them and what it calls each parameter is a fact about the
application, not about this game. Nothing here imports a host.
"""

from __future__ import annotations

from ...Kernel.bridge import cabmap_state
from . import cloth


def _prefab_texts(cabs):
    """The serialized text of what those archives carry -- what the cloth reader
    parses its fields out of. One published dataset, so there is no second way to
    open an archive on this side."""
    cabs = [cab for cab in cabs if cab]
    if not cabs or cabmap_state.BRIDGE is None:
        return []
    table = cabmap_state.BRIDGE.game_data("core.assets.text", cab=cabs)
    return [str(table.cell(index, "text")) for index in range(len(table))
            if str(table.cell(index, "path")).lower().endswith(".prefab")]


def read(cabs):
    """What those model prefabs state about their secondary motion, in the shared
    vocabulary (:mod:`Kernel.app.rigging`), or None for nothing to bring across.

    This is the callable the game module declares (see ``Game.GameModule``), so both
    ways in reach it without the host ever learning what these settings are -- only
    whether this game answered."""
    if cabmap_state.BRIDGE is None:
        return None
    texts = _prefab_texts(cabs)
    if not texts:
        return None
    reading = cloth.read(texts)
    return reading if reading["configs"] else None
