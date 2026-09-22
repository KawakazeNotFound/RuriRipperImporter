"""Every character the install ships, drawn by the ONE list kernel every game uses.

``unreal.characters`` states what the build ships as a cast, and a title whose own
design database files that cast under its own kinds says so on every row. WHICH
column carries the name, the id, the kind and the packages is not restated here:
each column says so itself, where the decoder builds it. So this module holds no
statement about the shape of that table at all -- the facet switch, the search, the
rule editor, the list, the sections and the status line are :mod:`Kernel.app.view`,
and a decoder that grows a kind or renames a column needs no edit anywhere here.

A row's payload is its seed -- the packages the decoder named for it, read whole by
its statement source -- so loading and revealing a row are the kernel's own verbs.
What is left is genuinely this engine's: decompiling the shaders its materials
compiled to has no counterpart anywhere else.

Nothing here imports a host.
"""

from __future__ import annotations

from ...Kernel import host as host_port
from ...Kernel.app import browser as app_browser
from ...Kernel.app import cast_panel
from ...Kernel.app import command, filtering
from ...Kernel.app import layout as app_layout
from ...Kernel.app import schemas
from ...Kernel.app import view as app_view
from ...Kernel.app.state import Schema
from ...Kernel.bridge import cabmap_state
from . import datasets

STATE = "ruri_unreal_characters"
SPEC_KEY = "UnrealEngine:characters"

#: This tab's live view, and the seats that draw it. Module state like the
#: browser's own caches: a draw never crosses the CLR boundary -- a command asks
#: for a new view and the seats redraw.
BOUND = app_view.Bound(SPEC_KEY)

#: The cast table as last read. Held only to ask it for views; nothing on this
#: side ever reads a column of it.
_TABLE = [None]


def state_of(context):
    return host_port.current().panel_state(context, STATE)


def table():
    return _TABLE[0]


CHARACTERS = Schema("UnrealCharacters", """This engine's cast tab states nothing
of its own: what a row is, and everything drawn around it, is the shared record.""",
                    (), include=(schemas.FILTER_STATE, schemas.LOADING_STATE,
                                 cast_panel.CAST_STATE))


def rebuild(state):
    """Ask the kernel for this list as it is now stated. Nothing is evaluated on
    this side -- the text, the rules and the facet go over as typed."""
    with filtering.rebuilding():
        BOUND.open(table(), state)


HANDLERS = cast_panel.handlers(BOUND, "SBUE.characters", rebuild)

FILTER_SPEC = filtering.register_spec(filtering.FilterSpec(
    key=SPEC_KEY, fields=BOUND.fields,
    state_for=state_of,
    apply=lambda context: rebuild(state_of(context))))


# ---------------------------------------------------------------------------
# What the buttons do
# ---------------------------------------------------------------------------
def _loaded(context):
    return app_browser.state_of(context).loaded and cabmap_state.BRIDGE is not None


def _refresh(context, arguments):
    """Read the cast this install ships off the decoder."""
    state = state_of(context)
    try:
        _TABLE[0] = datasets.cast()
    except Exception as exc:
        state.status = "{0}: {1}".format(type(exc).__name__, exc)
        return {"CANCELLED"}
    state.status = ""
    rebuild(state)
    cast_panel.opened(BOUND, state)
    return None


def _shaders(state, output):
    """This engine ships no shader ASSET: a material's program lives as blobs in an
    archive shared with everything else the build cooked. So it answers the shared
    button itself -- what lands on disk is the vertex and pixel stages as source,
    one file per variant."""
    seed = BOUND.payload(state)
    return datasets.shaders([seed], output) if seed else []


def _animation_rules(context, state):
    """Where this one's animations live, as the DECODER states it -- never guessed at on
    this side. ``unreal.characters.animations`` is answered per title (each build files
    its own animation content its own way; the family states no answer of its own, see
    UnrealDatasets.CharactersAnimations), keyed by this row's own id, the same id the
    cast list itself showed. An empty answer means the title has not stated one, or
    genuinely ships nothing for this row -- either way there is nothing to show."""
    entry = BOUND.picked(state)
    if entry is None:
        return None
    found = cabmap_state.BRIDGE.game_data("unreal.characters.animations", key=entry.key)
    if len(found) == 0:
        return None
    anchor = found.cell(0, "anchor")
    hits = found.cell(0, "hits")
    group = found.cell(0, "group")
    rules = [
        {"field": "container", "relation": "contains", "value": anchor, "action": "include"},
        {"field": "type_names", "relation": "contains", "value": "AnimationClip", "action": "include"},
    ]
    said = (
        "'{0}' ships no animation folder of its own; showing the shared '{1}' "
        "library it plays from ({2} rows).".format(entry.label, group, hits)
        if group else
        "{0}: {1} animation row(s).".format(entry.label, hits))
    return rules, said


REFRESH = command.COMMANDS.define(
    "ruri.unreal_characters_refresh", "List Characters", _refresh,
    description="Read the cast this install ships off the decoder",
    icon="FILE_REFRESH", internal=True, poll=_loaded)

#: Name, then the build's own id, then the build's own finer kind hard right --
#: which is what tells several rows sharing a display name apart. Each cell names
#: the ROLE it reads, never a column: one decoder answers for every Unreal build
#: and they do not file a cast under the same column names. Naming them outright
#: meant the list could not be drawn at all for a build without those columns.
_COLUMNS = (
    BOUND.column("", label="Name", width=0.4, icon="OUTLINER_OB_ARMATURE"),
    BOUND.role_column(app_view.KEY, label="Id", width=0.45, align=app_layout.RIGHT, enabled=False),
    BOUND.role_column(app_view.DETAIL, label="Type", align=app_layout.RIGHT, enabled=False),
)



PANEL = cast_panel.Panel(
    BOUND, _COLUMNS, "unreal_characters", REFRESH.id, state_of, STATE, shaders=_shaders,
    animation_rules=_animation_rules,
    # 这套引擎把表情记在网格自己的 morph 列表里,不是 Unity 的混合形状 —— 问的是同一个
    # 问题,所以画在同一格里,只是换成这个解码器说它的那份数据集。
    face_dataset=("unreal.morphtargets", "seed"),
)


def draw(layout, context):
    cast_panel.draw(PANEL, layout, context, state_of(context))


def register():
    host_port.current().register_state(
        STATE, CHARACTERS, HANDLERS, extra={"FILTER_SPEC_KEY": SPEC_KEY})


def unregister():
    host_port.current().unregister_state(STATE)
    cast_panel.forget(BOUND)
    BOUND.close()
    _TABLE[0] = None
