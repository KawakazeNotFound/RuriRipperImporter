"""What this game publishes, and nothing more.

Every row below is computed on the hook side and arrives columnar, already stating which column is
the key, the label, the group, the detail and the payload -- and the payload IS the row's seed, so
nothing here turns a row into archives. Arguments go by NAME and none of them says where the game is
installed: the session is opened on an install, so a caller states WHAT it wants and never WHERE.
"""

from __future__ import annotations

from ...Kernel.bridge import cabmap_state

CAST = "azurpromilia.roster.cast"
SCENES = "azurpromilia.scene.list"


def _table(dataset_id, **args):
    return cabmap_state.BRIDGE.game_data(dataset_id, **args)


def cast():
    """The cast, one row per outfit under the character it dresses."""
    return _table(CAST)


def scenes():
    """Every scene the install carries, with whether its built scene file is present."""
    return _table(SCENES)
