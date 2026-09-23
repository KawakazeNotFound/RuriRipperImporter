"""The volume sets the title's render pipeline puts its post chain under -- the world's own, the character
preview's, the display's -- and the grading each one gives it.

The list and every value behind it come from the hook: which prefabs are volume sets, how their volumes
blend, and what that stack becomes as the post stage's inputs. Applying a row hands those inputs to the
host's display chain as they are; nothing here reads an asset or knows what an input means.

Nothing here imports a host.
"""

from __future__ import annotations

from ...Kernel import host as host_port
from ...Kernel.app import browser as app_browser
from ...Kernel.app import command
from ...Kernel.app import layout as app_layout
from ...Kernel.app.state import Field, Schema
from ...Kernel.app import state as app_state
from ...Kernel.app import view as app_view
from ...Kernel.bridge import cabmap_state
from . import datasets

STATE = "ruri_azurpromilia_display"
SPEC_KEY = "AzurPromilia:display"

BOUND = app_view.Bound(SPEC_KEY)
_TABLE = {}


def state_of(context):
    return host_port.current().panel_state(context, STATE)


DISPLAY = Schema("AzurPromiliaDisplay", """The volume set browser's state.""", (
    Field("rows", app_state.COLLECTION, element=app_view.VIEW_ROW),
    Field("active_index", app_state.INT, 0),
    Field("status", app_state.STRING, "Load a cabmap, then refresh the volume sets."),
))

HANDLERS = app_state.Handlers("AzurPromilia.display")


def rebuild(state):
    BOUND.open(_TABLE.get("volumes"), state)


def _loaded(context):
    return app_browser.state_of(context).loaded and cabmap_state.BRIDGE is not None


def _refresh(context, arguments):
    """Read the volume sets the install's pipeline carries."""
    state = state_of(context)
    try:
        _TABLE["volumes"] = datasets.post_volumes()
    except Exception as exc:
        state.status = "{0}: {1}".format(type(exc).__name__, exc)
        return {"CANCELLED"}
    rebuild(state)
    state.status = "{0} volume set(s).".format(len(_TABLE["volumes"]))
    return None


REFRESH = command.COMMANDS.define(
    "ruri.azurpromilia_display_refresh", "Refresh Volume Sets", _refresh,
    description="Read the volume sets the install's render pipeline puts its post chain under",
    icon="FILE_REFRESH", poll=_loaded)


def _picked(context):
    entry = BOUND.picked(state_of(context))
    return entry.payload if entry is not None and entry.payload else None


def _apply(context, arguments):
    """Grade the scene's post chain the way the picked volume set grades the game's."""
    state = state_of(context)
    volume = _picked(context)
    try:
        written = host_port.current().apply_post_inputs(context, datasets.post_grading(volume))
    except Exception as exc:
        state.status = "{0}: {1}".format(type(exc).__name__, exc)
        return {"CANCELLED"}
    state.status = "{0}: {1} post input(s) set.".format(volume.rsplit("/", 1)[-1], written)
    return None


APPLY = command.COMMANDS.define(
    "ruri.azurpromilia_display_apply", "Apply Grading", _apply,
    description="Set the post chain's colour grading to what the picked volume set gives the game's",
    icon="SEQ_HISTOGRAM", poll=lambda context: _loaded(context) and _picked(context) is not None,
    requires=host_port.Compositor)


_COLUMNS = (
    BOUND.column("", width=0.45, icon="SEQ_HISTOGRAM"),
    BOUND.column("detail", align=app_layout.RIGHT, enabled=False),
)


def draw(layout, context):
    state = state_of(context)
    head = layout.row(align=True)
    head.label(text="Volume Sets", icon="SEQ_HISTOGRAM")
    head.operator(REFRESH.id, text="", icon="FILE_REFRESH")
    app_view.draw_list(BOUND, layout, state, _COLUMNS, "azurpromilia_volume_sets")
    layout.operator(APPLY.id)
    layout.label(text=state.status)


def register():
    host_port.current().register_state(STATE, DISPLAY, HANDLERS)


def unregister():
    host_port.current().unregister_state(STATE)
    BOUND.close()
    _TABLE.clear()
