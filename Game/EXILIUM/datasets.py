"""What this game publishes, and nothing more.

Every row below is computed on the hook side and arrives columnar, already
searchable under its own handle. Nothing here parses a byte of the game: this
title states its models by name in protobuf config tables, hides every address
behind a hash of the asset path, and packs most of its archives inside other
archives -- three facts that live in ``Ruri.RipperHook.EXILIUM`` and nowhere else.

Arguments go by NAME and none of them says where the game is installed: the
session is opened on an install and the hook declares which folders under it hold
content, so a caller states WHAT it wants and never WHERE.
"""

from __future__ import annotations

from ...Kernel.bridge import cabmap_state

LANGUAGE = "exilium.roster.language"
CAST = "exilium.roster.cast"
SCENES = "exilium.scene.list"

# The two casts the game publishes. A panel states WHICH cast it wants, never how
# one is read.
CHARACTERS = "Characters"
MODELS = "Models"


def _table(dataset_id, **args):
    return cabmap_state.BRIDGE.game_data(dataset_id, **args)


def _rows(dataset_id, **args):
    table = _table(dataset_id, **args)
    return [{name: table.cell(index, name) for name in table.names}
            for index in range(len(table))]


def language_for_locale(locale=""):
    """The text package a host locale reads through. Which packages exist, and
    which locale lands on which, are the game's own facts."""
    rows = _rows(LANGUAGE, locale=str(locale or ""))
    return rows[0]["language"] if rows else ""


def cast(language):
    """The WHOLE cast as one table: kind/key/label/group/detail plus the game's own
    columns to filter on. One table because it is one list -- which half a row is,
    is its ``kind``, and narrowing by that is the facet switch every list has."""
    return _table(CAST, language=language)

def scenes():
    """Every scene the game ships, under the path its own catalog states."""
    return _table(SCENES)
