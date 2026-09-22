"""Browse the game's cast the way the game itself lists it -- in any host.

Two panes over one dataset: ``Characters`` are the units the game lets you field,
named through whichever text package the HOST's own locale reads (so switching the
application's language switches the roster with no reload of anything else);
``Models`` is every model the config declares -- a character's outfits, the
enemies, the summons -- each already resolved to the address the catalog knows it
by.

The list behaves like the bundle browser next door: type to filter, click to
select, and Load and Reveal are the kernel's verbs over the row's payload -- its
seed, which the hook's statement source reads as the archives the address spans and
the meshes its renderers are filled with at run time.

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

STATE = "ruri_exilium_roster"
SPEC_KEY = "EXILIUM:character"

CHARACTERS = datasets.CHARACTERS
MODELS = datasets.MODELS

#: Loaded row tables, by (kind, language). Module scope, not panel state:
#: rebuilding the drawn list must not cost a re-read, and a column table is not
#: something a host's property system can hold anyway.
_ROWS = {}


def state_of(context):
    return host_port.current().panel_state(context, STATE)


# ---------------------------------------------------------------------------
# What the panel remembers
# ---------------------------------------------------------------------------
#: This tab's live view and the seats that draw it. The kind is not a facet:
#: this game keeps its two casts in two tables, so the switch picks the TABLE
#: and the view narrows nothing. Which column is the name, the id, the role or
#: the "downloaded" test is each column's own statement, made in the hook.
BOUND = app_view.Bound(SPEC_KEY)

ROSTER = Schema("ExiliumRoster", """What this game's cast tab remembers beyond
the shared record: which text package it read the names through.""", (
    Field("language", app_state.STRING, ""),
), include=(schemas.FILTER_STATE, schemas.LOADING_STATE, cast_panel.CAST_STATE))




FILTER_SPEC = filtering.register_spec(filtering.FilterSpec(
    key=SPEC_KEY, fields=BOUND.fields,
    state_for=state_of,
    apply=lambda context: rebuild(state_of(context))))


# ---------------------------------------------------------------------------
# The rows
# ---------------------------------------------------------------------------
def language(state):
    return datasets.language_for_locale("")


def rows(state):
    return _ROWS.get(language(state))


def rebuild(state):
    """Rebuild the drawn line list.

    The filter is NOT evaluated here: the search text and the Include/Exclude rules
    go to the same C# engine the bundle browser searches with, over the very buffers
    this table was built from. This side receives row ids and reads cells."""
    with filtering.rebuilding():
        BOUND.open(rows(state), state, note=language(state))


HANDLERS = cast_panel.handlers(BOUND, "EXILIUM.roster", rebuild)


# ---------------------------------------------------------------------------
# What the buttons do
# ---------------------------------------------------------------------------
def _loaded(context):
    return app_browser.state_of(context).loaded and cabmap_state.BRIDGE is not None


def _has_selection(context):
    return _loaded(context) and BOUND.picked(state_of(context)) is not None


def _refresh(context, arguments):
    """Read the cast out of the game's own config tables."""
    state = state_of(context)
    tongue = language(state)
    state.language = tongue
    try:
        table = datasets.cast(tongue)
    except Exception as exc:
        state.status = "{0}: {1}".format(type(exc).__name__, exc)
        return {"CANCELLED"}
    _ROWS[tongue] = table
    rebuild(state)
    cast_panel.opened(BOUND, state)
    return None


def _outfits(context, arguments):
    """List the selected character's own models, in the Models pane."""
    state = state_of(context)
    entry = BOUND.picked(state)
    if entry is None:
        return {"CANCELLED"}
    wanted = entry.key
    state.facet = MODELS
    if rows(state) is None:
        _refresh(context, {})
    state.filter_rules.clear()
    rule = state.filter_rules.add()
    # A rule offers the fields of the list it belongs to, and it learns which list
    # that is from its own spec_key -- stamp it before naming a field, or the enum
    # still holds the empty fallback vocabulary and the assignment raises.
    rule.spec_key = SPEC_KEY
    rule.field = "character"
    rule.relation = "is"
    rule.value = wanted
    rule.action = "include"
    rule.enabled = True
    rebuild(state)
    return None


def _outfits_poll(context):
    """Only a CHARACTER has models of her own to show -- which the picked row says
    itself, in the game's own filing."""
    if not _has_selection(context):
        return False
    entry = BOUND.picked(state_of(context))
    return entry is not None and entry.cell("kind") == CHARACTERS


REFRESH = command.COMMANDS.define(
    "ruri.exilium_roster_refresh", "Refresh Roster", _refresh,
    description="Read the cast out of the game's own config tables",
    icon="FILE_REFRESH", poll=_loaded)
OUTFITS = command.COMMANDS.define(
    "ruri.exilium_roster_outfits", "Show Outfits", _outfits,
    description="Switch to the Models pane and list only the models this one wears",
    icon="MOD_CLOTH", poll=_outfits_poll)


# ---------------------------------------------------------------------------
# What it looks like
# ---------------------------------------------------------------------------
#: A cast row: the name, the id when the game gives it one of its own, and
#: whatever detail that projection carries. A row the install never downloaded is
#: dimmed rather than hidden while the filter says to show it -- it is real data
#: with nothing behind it here.
_COLUMNS = (
    BOUND.column("", width=0.55,
                 icon=lambda seat: ("OUTLINER_OB_ARMATURE" if BOUND.shipped(seat)
                                    else "LIBRARY_DATA_BROKEN"),
                 active=BOUND.shipped),
    BOUND.key_column("({0})", width=0.5, enabled=False),
    BOUND.column("detail", align=app_layout.RIGHT, enabled=False),
)
_GROUP_COLUMN = BOUND.column("", icon="OUTLINER_COLLECTION")



PANEL = cast_panel.Panel(
    BOUND, _COLUMNS, "exilium_roster", REFRESH.id, state_of, STATE,
    group_column=_GROUP_COLUMN, actions=(OUTFITS.id,), facet=CHARACTERS)


def draw(layout, context):
    cast_panel.draw(PANEL, layout, context, state_of(context))


def register():
    host_port.current().register_state(
        STATE, ROSTER, HANDLERS, extra={"FILTER_SPEC_KEY": SPEC_KEY})


def unregister():
    host_port.current().unregister_state(STATE)
    cast_panel.forget(BOUND)
    BOUND.close()
    _ROWS.clear()
