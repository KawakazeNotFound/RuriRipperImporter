"""A character is ASSEMBLED, not shipped: one skeleton plus a prefab per slot.

WHICH pieces, in what order, on which bone and with what correction is the hook's
answer (the ``chara.plan`` dataset, keyed by the card and the outfit), and so is the
seed that loads her: the row's own payload is the card in its first outfit with
every slot, and the outfit and the families of pieces picked here are asked of the
hook as the seed of exactly those choices (``chara.seed``). Loading is the kernel's
verb over that seed; what "assemble" MEANS is the reader's statement and the host's
building. What does not cross is driving her FACE and her ANIMATIONS, which are the
other two sections and say so with their own capabilities.

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

STATE = "ruri_kk_chara"
SPEC_KEY = "Illusion:cast"

#: The seven outfits the game's own customization slots are numbered by.
COORDINATES = ("School01", "School02", "Gym", "Swim", "Club", "Plain", "Pajamas")


def state_of(context):
    return host_port.current().panel_state(context, STATE)


# ---------------------------------------------------------------------------
# What the panel remembers
# ---------------------------------------------------------------------------
#: This tab's live view and the seats that draw it. WHICH column is the name, the
#: id, the section or the outfit count is not stated here -- each column says so
#: itself, where the hook builds the cast.
BOUND = app_view.Bound(SPEC_KEY)

CHARA = Schema("IllusionChara", """What this family's cast tab remembers beyond
the shared record: which outfit to build her in, and which families of pieces.""", (
    Field("coordinate", app_state.ENUM, "0", "Outfit",
          "Which of the character's seven outfits to build",
          items=tuple((str(index), name, "The character's {0} outfit".format(name))
                      for index, name in enumerate(COORDINATES))),
    Field("build_hair", app_state.BOOL, True, "Hair"),
    Field("build_clothes", app_state.BOOL, True, "Clothes"),
    Field("build_accessories", app_state.BOOL, True, "Accessories"),
), include=(schemas.FILTER_STATE, schemas.LOADING_STATE, cast_panel.CAST_STATE))



FILTER_SPEC = filtering.register_spec(filtering.FilterSpec(
    key=SPEC_KEY, fields=BOUND.fields,
    state_for=state_of,
    apply=lambda context: rebuild(state_of(context))))


# ---------------------------------------------------------------------------
# The rows
# ---------------------------------------------------------------------------
def selected_card(state):
    """The picked card's own path -- the row's key, which is what the plan is asked by."""
    entry = BOUND.picked(state)
    return entry.key if entry is not None else ""


def plan(state):
    """Every piece the selected card wears in the selected outfit, as the hook
    resolved it."""
    card = selected_card(state)
    if not card:
        return []
    return datasets.rows(datasets.PLAN, cardPath=card, outfit=int(state.coordinate))


def wanted_plan(state):
    """The pieces the toggles ask for. The rig, the body and the head are never
    optional -- a character without them is not a lighter build, it is a broken
    one."""
    wanted = {"armature", "head_armature", "body", "tongue", datasets.HEAD}
    if state.build_hair:
        wanted.add(datasets.HAIR)
    if state.build_clothes:
        wanted.update((datasets.CLOTHES, datasets.SUB_CLOTHES))
    if state.build_accessories:
        wanted.add(datasets.ACCESSORY)
    return [part for part in plan(state) if part["slot"] in wanted]


def rebuild(state):
    with filtering.rebuilding():
        table = datasets.table(datasets.CAST)
        if table is None:
            state.status = datasets.why_empty(datasets.CAST) or "Load a cabmap, then refresh."
        BOUND.open(table, state)


HANDLERS = cast_panel.handlers(BOUND, "Illusion.chara", rebuild)



# ---------------------------------------------------------------------------
# What the buttons do
# ---------------------------------------------------------------------------
def _loaded(context):
    return app_browser.state_of(context).loaded and cabmap_state.BRIDGE is not None


def _refresh(context, arguments):
    """Read the game's customization catalog and its character cards."""
    state = state_of(context)
    try:
        datasets.table(datasets.CAST, refresh=True)
    except Exception as exc:
        state.status = "{0}: {1}".format(type(exc).__name__, exc)
        return {"CANCELLED"}
    rebuild(state)
    cast_panel.opened(BOUND, state)
    return None


def _seed(_context, state, _payload):
    """The seed of the picked card in the chosen outfit, wearing the families of pieces the
    toggles ask for -- spelled by the hook, over the slots its own plan names."""
    card = selected_card(state)
    if not card:
        return ""
    slots = sorted({part["slot"] for part in wanted_plan(state)})
    rows = datasets.rows(datasets.SEED, cardPath=card, outfit=int(state.coordinate), slot=slots)
    return str(rows[0]["seed"]) if rows else ""


REFRESH = command.COMMANDS.define(
    "ruri.kk_chara_refresh", "Refresh Characters", _refresh,
    description="Read the game's customization catalog and its character cards",
    icon="FILE_REFRESH", poll=_loaded)


# ---------------------------------------------------------------------------
# What it looks like
# ---------------------------------------------------------------------------
_COLUMNS = (
    BOUND.column("", width=0.7, icon="OUTLINER_OB_ARMATURE"),
    BOUND.column("file", align=app_layout.RIGHT, enabled=False),
)
_GROUP_COLUMN = BOUND.column("", icon="OUTLINER_COLLECTION")


def _options(layout, context, state):
    """What this game adds under its cast list: which outfit she wears, which
    families of pieces to build, and what that comes to."""
    layout.prop(state, "coordinate")
    toggles = layout.row(align=True)
    toggles.prop(state, "build_hair", toggle=True)
    toggles.prop(state, "build_clothes", toggle=True)
    toggles.prop(state, "build_accessories", toggle=True)
    if not selected_card(state):
        return
    rows = plan(state)
    counts = {}
    for part in rows:
        counts[part["slot"]] = counts.get(part["slot"], 0) + 1
    box = layout.box()
    box.label(text="{0} part(s) from {1} bundle(s)".format(
        len(rows), len({part["bundle"] for part in rows})))
    box.label(text=", ".join("{0} {1}".format(count, slot)
                             for slot, count in sorted(counts.items())))


def _draw_catalog(layout, context):
    """The studio's own animation catalog, in the shape its own kinds need -- an
    ordinary animation one per row, an H act as two partners side by side."""
    from . import anime
    anime.draw(layout, context)


PANEL = cast_panel.Panel(
    BOUND, _COLUMNS, "illusion_cast", REFRESH.id, state_of, STATE,
    group_column=_GROUP_COLUMN, options=_options, seed=_seed,
    animations=(cast_panel.Source("catalog", "Catalog",
                                  "Every animation the studio catalogs, under its own "
                                  "names -- an H act as two partners side by side",
                                  _draw_catalog),))


def draw_tab(layout, context):
    cast_panel.draw(PANEL, layout, context, state_of(context))


def register():
    host_port.current().register_state(
        STATE, CHARA, HANDLERS, extra={"FILTER_SPEC_KEY": SPEC_KEY})


def unregister():
    host_port.current().unregister_state(STATE)
    cast_panel.forget(BOUND)
    BOUND.close()
