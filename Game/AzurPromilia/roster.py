"""Browse this game's cast -- one row per outfit, under the character it dresses -- in any host.

A row's payload is its seed, spelled on the hook side, so loading a row, revealing it and asking
what it shades with are the kernel's verbs over that seed. This module names the list and how it
is drawn, and nothing else.

Nothing here imports a host.
"""

from __future__ import annotations

from ...Kernel import host as host_port
from ...Kernel.app import browser as app_browser
from ...Kernel.app import cast_panel
from ...Kernel.app import command, filtering
from ...Kernel.app import layout as app_layout
from ...Kernel.app import schemas
from ...Kernel.app.state import Schema
from ...Kernel.app import view as app_view
from ...Kernel.bridge import cabmap_state
from . import datasets

STATE = "ruri_azurpromilia_roster"
SPEC_KEY = "AzurPromilia:character"

#: The loaded cast table. Module scope, not panel state: rebuilding the drawn list must not cost a
#: re-read, and a column table is not something a host's property system can hold anyway.
_TABLES = {}


def state_of(context):
    return host_port.current().panel_state(context, STATE)


BOUND = app_view.Bound(SPEC_KEY)

ROSTER = Schema("AzurPromiliaRoster", """What this game's cast tab remembers: the shared
record, and nothing of its own.""", (),
                include=(schemas.FILTER_STATE, schemas.LOADING_STATE, cast_panel.CAST_STATE))


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


def _loaded(context):
    return app_browser.state_of(context).loaded and cabmap_state.BRIDGE is not None


def _refresh(context, arguments):
    """Read the cast off the game's own tables."""
    state = state_of(context)
    try:
        _TABLES["cast"] = datasets.cast()
    except Exception as exc:
        state.status = "{0}: {1}".format(type(exc).__name__, exc)
        return {"CANCELLED"}
    rebuild(state)
    cast_panel.opened(BOUND, state)
    return None


REFRESH = command.COMMANDS.define(
    "ruri.azurpromilia_roster_refresh", "Refresh Roster", _refresh,
    description="Read the cast off the game's own tables",
    icon="FILE_REFRESH", poll=_loaded)


#: A cast row: the character, and the outfit it wears.
_COLUMNS = (
    BOUND.column("", width=0.55,
                 icon=lambda seat: ("OUTLINER_OB_ARMATURE" if BOUND.shipped(seat)
                                    else "LIBRARY_DATA_BROKEN"),
                 active=BOUND.shipped),
    BOUND.column("detail", align=app_layout.RIGHT, enabled=False),
)
_GROUP_COLUMN = BOUND.column("", icon="OUTLINER_COLLECTION")

PANEL = cast_panel.Panel(
    BOUND, _COLUMNS, "azurpromilia_roster", REFRESH.id, state_of, STATE,
    group_column=_GROUP_COLUMN)


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
