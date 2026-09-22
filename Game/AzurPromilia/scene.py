"""Every scene the install carries, under the folder tree the game files it in.

A row says whether the BUILT scene file is present: this title rarely ships the built ``.unity``
with its packages, so most scenes arrive as terrain, materials and colliders only. A row without
one is dimmed rather than hidden -- its resources are real and loading them is a real act, it just
is not the scene itself.

Picking one and pressing Load runs the bundle browser's own import over the archives that address
resolved to, which is why this tab needs nothing of the host the browser does not already need.

Nothing here imports a host.
"""

from __future__ import annotations

from ...Kernel import host as host_port
from ...Kernel.app import browser as app_browser
from ...Kernel.app import command, filtering
from ...Kernel.app import layout as app_layout
from ...Kernel.app import schemas
from ...Kernel.app.state import Field, Schema
from ...Kernel.app import state as app_state
from ...Kernel.app import view as app_view
from ...Kernel.bridge import cabmap_state
from . import datasets, roster

STATE = "ruri_azurpromilia_scene"
SPEC_KEY = "AzurPromilia:scene"

BOUND = app_view.Bound(SPEC_KEY)
_TABLE = {}


def state_of(context):
    return host_port.current().panel_state(context, STATE)


SCENE = Schema("AzurPromiliaScene", """The scene browser's whole state.""", (
    Field("search", app_state.STRING, "", "Filter",
          "Filter by scene name or folder",
          update="on_filter_edit", live=True),
    Field("rows", app_state.COLLECTION, element=app_view.VIEW_ROW),
    Field("active_index", app_state.INT, 0),
    Field("status", app_state.STRING, "Load a cabmap, then refresh the scene list."),
    Field("built_only", app_state.BOOL, False, "Built only",
          "Hide the scenes this install carries resources for but no built scene file"),
), include=(schemas.FILTER_STATE, schemas.LOADING_STATE))


def _on_filter_edit(state, context):
    rebuild(state)


HANDLERS = app_state.Handlers(
    "AzurPromilia.scene", base=filtering.HANDLERS, on_filter_edit=_on_filter_edit)


FILTER_SPEC = filtering.register_spec(filtering.FilterSpec(
    key=SPEC_KEY, fields=BOUND.fields,
    state_for=state_of,
    apply=lambda context: rebuild(state_of(context))))


def rebuild(state):
    """Ask the kernel for the drawn list as it is now stated. The search text, the rules, the
    sections and the truncation are all answered on the other side."""
    with filtering.rebuilding():
        BOUND.open(_TABLE.get("scenes"), state)


# ---------------------------------------------------------------------------
# What the buttons do
# ---------------------------------------------------------------------------
def _loaded(context):
    return app_browser.state_of(context).loaded and cabmap_state.BRIDGE is not None


def _has_selection(context):
    return _loaded(context) and BOUND.picked(state_of(context)) is not None


def _refresh(context, arguments):
    """Read every scene the install carries."""
    state = state_of(context)
    try:
        _TABLE["scenes"] = datasets.scenes()
    except Exception as exc:
        state.status = "{0}: {1}".format(type(exc).__name__, exc)
        return {"CANCELLED"}
    rebuild(state)
    return None


def _load(context, arguments):
    """Import the selected scene through the browser's own import -- one import path, so a fix
    there is a fix here."""
    entry = BOUND.picked(state_of(context))
    if entry is None:
        return
    yield from roster.load_address(context, entry.key, entry.label)


def _reveal(context, arguments):
    entry = BOUND.picked(state_of(context))
    if entry is None:
        return {"CANCELLED"}
    return roster.reveal_address(context, entry.key, entry.label)


REFRESH = command.COMMANDS.define(
    "ruri.azurpromilia_scene_refresh", "Refresh Scenes", _refresh,
    description="Read the scene list off the install's own folder tree",
    icon="FILE_REFRESH", poll=_loaded)
LOAD = command.COMMANDS.define(
    "ruri.azurpromilia_scene_load", "Load Scene", _load,
    description="Import this scene, exactly as the bundle browser would",
    icon="IMPORT", poll=_has_selection, steps=True, status_state=STATE,
    failure="Loading this scene failed")
REVEAL = command.COMMANDS.define(
    "ruri.azurpromilia_scene_reveal", "Open Containing Folder", _reveal,
    description="Switch to the bundle browser and open where this scene lives",
    icon="FILE_FOLDER", poll=_has_selection)


#: A scene row. Filtering already happened against the table's own fields, so no row is hidden at
#: draw time.
_COLUMNS = (
    BOUND.column("", width=0.7, icon="SCENE_DATA"),
    BOUND.column("detail", align=app_layout.RIGHT, enabled=False),
)
_GROUP_COLUMN = BOUND.column("", icon="OUTLINER_COLLECTION")


def draw(layout, context):
    state = state_of(context)

    command.draw_progress(layout, state)
    head = layout.row(align=True)
    head.label(text="Scenes", icon="SCENE_DATA")
    head.operator(REFRESH.id, text="", icon="FILE_REFRESH")

    filtering.draw_search_row(layout, state)
    app_view.draw_list(BOUND, layout, state, _COLUMNS, "azurpromilia_scenes",
                       group_column=_GROUP_COLUMN)

    options = layout.column(align=True)
    app_browser.draw_import_options(options, context)
    actions = options.column(align=True)
    actions.enabled = BOUND.picked(state) is not None
    actions.operator(LOAD.id)
    actions.operator(REVEAL.id)


def register():
    host_port.current().register_state(
        STATE, SCENE, HANDLERS, extra={"FILTER_SPEC_KEY": SPEC_KEY})


def unregister():
    host_port.current().unregister_state(STATE)
    BOUND.close()
    _TABLE.clear()
