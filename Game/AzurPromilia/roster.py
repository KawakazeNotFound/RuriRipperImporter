"""Browse this game's cast the way its own asset tree files it -- in any host.

This title ships no roster asset: a character id is a LEVEL of the address tree, and the rig family
above it is another, so a row is one (rig, character). The hook reads that; this side picks a row.

Loading is deliberately not its own importer. A row's key IS an address, the loaded map says which
archives sit under it, and those go into the bundle browser's own selection before its own import
runs -- so a fix over there is a fix here.

Nothing here imports a host.
"""

from __future__ import annotations

from ...Kernel import host as host_port
from ...Kernel.app import browser as app_browser
from ...Kernel.app import cast_panel
from ...Kernel.app import command, filtering
from ...Kernel.app import layout as app_layout
from ...Kernel.app import schemas
from ...Kernel.app.state import Field, Schema
from ...Kernel.app import state as app_state
from ...Kernel.app import view as app_view
from ...Kernel.bridge import cabmap_state
from . import datasets

STATE = "ruri_azurpromilia_roster"
SPEC_KEY = "AzurPromilia:character"

#: The loaded cast table and, per picked character, its parts. Module scope, not panel state:
#: rebuilding the drawn list must not cost a re-read, and a column table is not something a host's
#: property system can hold anyway.
_TABLES = {}


def state_of(context):
    return host_port.current().panel_state(context, STATE)


BOUND = app_view.Bound(SPEC_KEY)

ROSTER = Schema("AzurPromiliaRoster", """What this game's cast tab remembers beyond the shared
record: which character the parts list below was read for.""", (
    Field("parts_of", app_state.STRING, ""),
), include=(schemas.FILTER_STATE, schemas.LOADING_STATE, cast_panel.CAST_STATE))


def rows(_state):
    return _TABLES.get("cast")


def rebuild(state):
    """Ask the kernel for the drawn list as it is now stated. The search text, the rules, the
    sections and the truncation are all answered on the other side."""
    with filtering.rebuilding():
        BOUND.open(rows(state), state)


HANDLERS = cast_panel.handlers(BOUND, "AzurPromilia.roster", rebuild)

FILTER_SPEC = filtering.register_spec(filtering.FilterSpec(
    key=SPEC_KEY, fields=BOUND.fields,
    state_for=state_of,
    apply=lambda context: rebuild(state_of(context))))


# ---------------------------------------------------------------------------
# What the buttons do
# ---------------------------------------------------------------------------
def _loaded(context):
    return app_browser.state_of(context).loaded and cabmap_state.BRIDGE is not None


def _has_selection(context):
    return _loaded(context) and BOUND.picked(state_of(context)) is not None


def _refresh(context, arguments):
    """Read the cast off the game's own asset tree."""
    state = state_of(context)
    try:
        _TABLES["cast"] = datasets.cast()
    except Exception as exc:
        state.status = "{0}: {1}".format(type(exc).__name__, exc)
        return {"CANCELLED"}
    rebuild(state)
    cast_panel.opened(BOUND, state)
    return None


def archives_for(address):
    """Which archives one address IS. The map answers it; this game adds nothing to the question."""
    return [row["cab"] for row in datasets.archives_under(address) if row["cab"]]


def archives_of_character(key):
    """Which archives one character IS.

    Not a folder: this game files a character's parts under DIFFERENT part trunks
    (``Mesh/Cloth/<id>/…`` and ``Mesh/Head/<id>/…`` are siblings), so there is no one address
    holding all of it. The parts table already answers per part, archive included, so the set is
    read off that rather than composed here out of assumptions about the tree.
    """
    table = datasets.parts(key)
    seen = []
    for index in range(len(table)):
        cab = table.cell(index, "cab")
        if cab and cab not in seen:
            seen.append(cab)
    return seen


def load_address(context, address, label):
    """Put whatever sits under one address into the browser's own selection and run its own import,
    as steps. Shared with the Scene tab, because "load this one thing" is the same act whether the
    thing is a character or a scene."""
    state = state_of(context)
    if not address:
        state.status = "'{0}' states no address.".format(label)
        return
    cabs = yield command.Read(lambda: archives_for(address), 0.2)
    if not cabs:
        state.status = "'{0}' is in the tree but this install carries no archive under it.".format(label)
        return
    cabmap_state.clear_selection()
    for cab in cabs:
        cabmap_state.SELECTED_CABS.add(cab)
    yield from app_browser.IMPORT_SELECTED.run(context, {"reset_scene": False})
    state.status = "Loaded '{0}' from {1} archive(s).".format(label, len(cabs))


def reveal_address(context, address, fallback):
    """Reveal what one address holds, over in the bundle browser."""
    reveal = command.COMMANDS.get("ruri.cabmap_reveal")
    for row in (datasets.archives_under(address) if address else []):
        if row["cab"]:
            return reveal.run(context, {"query": row["container"], "cab": row["cab"], "folder": ""})
    return reveal.run(context, {"query": fallback, "cab": "", "folder": ""})


def _load(context, arguments):
    """Bring in every part this character is assembled from."""
    entry = BOUND.picked(state_of(context))
    if entry is None:
        return
    state = state_of(context)
    cabs = yield command.Read(lambda: archives_of_character(entry.key), 0.2)
    if not cabs:
        state.status = "'{0}' lists no part this install carries.".format(entry.label)
        return
    cabmap_state.clear_selection()
    for cab in cabs:
        cabmap_state.SELECTED_CABS.add(cab)
    yield from app_browser.IMPORT_SELECTED.run(context, {"reset_scene": False})
    state.status = "Loaded '{0}' from {1} archive(s).".format(entry.label, len(cabs))


def _first_part_address(key):
    """One address this character owns, for the buttons that reveal rather than load."""
    table = datasets.parts(key)
    return table.cell(0, "key") if len(table) else ""


def _reveal(context, arguments):
    entry = BOUND.picked(state_of(context))
    if entry is None:
        return {"CANCELLED"}
    return reveal_address(context, _first_part_address(entry.key), entry.label)


def _seeds(_context, state):
    """What the picked one IS, as archive names -- the same set Load seeds with, so what the shared
    buttons read about a row is what loading that row would read."""
    entry = BOUND.picked(state)
    return [] if entry is None else archives_of_character(entry.key)


REFRESH = command.COMMANDS.define(
    "ruri.azurpromilia_roster_refresh", "Refresh Roster", _refresh,
    description="Read the cast off the game's own asset tree",
    icon="FILE_REFRESH", poll=_loaded)
LOAD = command.COMMANDS.define(
    "ruri.azurpromilia_roster_load", "Load Character", _load,
    description="Import every part filed under this character, exactly as the bundle browser would",
    icon="IMPORT", poll=_has_selection, steps=True, status_state=STATE,
    failure="Loading this character failed")
REVEAL = command.COMMANDS.define(
    "ruri.azurpromilia_roster_reveal", "Open Containing Folder", _reveal,
    description="Switch to the bundle browser and open where this character's assets live",
    icon="FILE_FOLDER", poll=_has_selection)


#: A cast row: the character, the rig family it is built on, and how much of it there is.
_COLUMNS = (
    BOUND.column("", width=0.55,
                 icon=lambda seat: ("OUTLINER_OB_ARMATURE" if BOUND.shipped(seat)
                                    else "LIBRARY_DATA_BROKEN"),
                 active=BOUND.shipped),
    BOUND.column("detail", align=app_layout.RIGHT, enabled=False),
)
_GROUP_COLUMN = BOUND.column("", icon="OUTLINER_COLLECTION")

PANEL = cast_panel.Panel(
    BOUND, _COLUMNS, "azurpromilia_roster", REFRESH.id, state_of, STATE, seeds=_seeds,
    group_column=_GROUP_COLUMN, actions=(LOAD.id, REVEAL.id))


def draw(layout, context):
    cast_panel.draw(PANEL, layout, context, state_of(context))


def register():
    host_port.current().register_state(
        STATE, ROSTER, HANDLERS, extra={"FILTER_SPEC_KEY": SPEC_KEY})


def unregister():
    host_port.current().unregister_state(STATE)
    cast_panel.forget(BOUND)
    BOUND.close()
    _TABLES.clear()
