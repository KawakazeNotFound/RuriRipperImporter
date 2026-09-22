"""What this game publishes, and nothing more.

Every row below is computed on the hook side and arrives columnar, already stating which column is
the key, the label, the group and the detail. Nothing here parses a byte of the game: this title
ships no roster asset at all -- the character id is a LEVEL of the asset tree -- and that reading
lives in ``Ruri.RipperHook.AzurPromilia`` and nowhere else.

Resolving one address to the archives holding it is not this game's business either: the loaded map
answers it for every title, so that call is the CORE selection set rather than a copy of it here.

Arguments go by NAME and none of them says where the game is installed: the session is opened on an
install and the hook declares which folders under it hold content, so a caller states WHAT it wants
and never WHERE.
"""

from __future__ import annotations

from ...Kernel.bridge import cabmap_state

CAST = "azurpromilia.roster.cast"
PARTS = "azurpromilia.model.parts"
SCENES = "azurpromilia.scene.list"

#: The map's own selection set -- one row per (cab, path) for whatever the rules match.
SELECT = "core.select"


def _table(dataset_id, **args):
    return cabmap_state.BRIDGE.game_data(dataset_id, **args)


def _rows(dataset_id, **args):
    table = _table(dataset_id, **args)
    return [{name: table.cell(index, name) for name in table.names}
            for index in range(len(table))]


def cast():
    """Every character the install carries, one row per (rig, character)."""
    return _table(CAST)


def parts(character):
    """What one character is assembled from. ``character`` is a roster row's own key, so the
    roster's identity travels unchanged rather than being taken apart here."""
    return _table(PARTS, character=str(character or ""))


def scenes():
    """Every scene the install carries, with whether its built scene file is present."""
    return _table(SCENES)


def archives_under(address):
    """The archives holding everything at or under one address.

    A part is one asset and a scene is a folder of them, so the same call answers both: the rule is
    a prefix over the map's own container field, which is the map's vocabulary, not this game's.
    """
    address = str(address or "")
    if not address:
        return []
    return _rows(SELECT, rule=["container|starts|" + address])
