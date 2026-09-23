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
POST_VOLUMES = "azurpromilia.post.volumes"
POST_GRADING = "azurpromilia.post.grading"


def _table(dataset_id, **args):
    return cabmap_state.BRIDGE.game_data(dataset_id, **args)


def cast():
    """The cast, one row per outfit under the character it dresses."""
    return _table(CAST)


def scenes():
    """Every scene the install carries, with whether its built scene file is present."""
    return _table(SCENES)


def post_volumes():
    """The volume sets the title's pipeline puts a post chain under."""
    return _table(POST_VOLUMES)


def post_grading(volume):
    """What one volume set grades the post chain with, keyed by the post stage's own input names: a
    scalar input as a float, a vector input's components as a tuple, an image input's texels as a
    list. The hook states each input one component per row, in order."""
    table = _table(POST_GRADING, volume=volume)
    components = {}
    images = set()
    for name, image, value in zip(table.values("input"), table.values("image"), table.values("value")):
        components.setdefault(name, []).append(float(value))
        if image:
            images.add(name)
    return {name: (values if name in images else values[0] if len(values) == 1 else tuple(values))
            for name, values in components.items()}
