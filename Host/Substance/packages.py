"""Build what a game resolved, with a Painter project.

The Blender materialiser next door turns the same selection into a skeleton,
meshes and node materials. Painter's answer to the identical description is one
self-contained mesh file plus a wired Texture Set per material, because that is
what Painter's entry point is -- ``project.create`` takes a path, and there is no
in-memory geometry API.

The difference is real, not a shortfall on either side, and it is stated exactly
here: the panel that asked said WHAT the thing is and nothing about how to build
one. What the thing IS comes from the reader as one statement, the same one
Blender gets -- a skeleton in it is simply a part this application has nowhere to
put, and the meshes and materials are the same surfaces to paint.
"""

from __future__ import annotations

from ...Kernel import statement as kernel_statement
from ...Kernel.app import loading
from ...Kernel.bridge import cabmap_state
from . import materialise as materialiser


def seeds_of(packages):
    """What to ask the reader about: the window's own seed paths where it has
    them, the addressable paths otherwise, and the archives as the last word."""
    if getattr(packages, "seed", ""):
        return [packages.seed]
    window = packages.window or {}
    seeds = [path for path in (window.get("seeds") or []) if path]
    if seeds:
        return sorted(set(seeds))
    paths = [path for path in (packages.paths or {}).values() if path]
    if paths:
        return sorted(set(paths))
    return [cab for cab in packages.cabs if cab]


def statement_for(seeds, options=None):
    """The statement these seeds make, in the basis this application writes and
    with the containers it can decode."""
    from ...Kernel import host as host_port

    host = host_port.current()
    values = dict(options or {})
    return kernel_statement.Statement.of(
        seeds,
        basis=str(getattr(host, "BASIS", "") or "gltf"),
        detail=int(values.get("detail_level", 0) or 0),
        inactive=bool(values.get("import_inactive", True)),
        shadow_proxies=bool(values.get("import_shadow_proxies", False)),
        containers=list(host.texture_containers() or ()),
        roles=_role_layers())


def materialise(context, packages, options=None, report=None, resolved=None):
    """Import one resolved thing into a Painter project."""
    lines = report if report is not None else []
    if cabmap_state.BRIDGE is None:
        return loading.Built(warnings=["No cabmap session is open."])
    seeds = seeds_of(packages)
    if not seeds:
        return loading.Built(warnings=[
            "The game states no packages for '{0}'.".format(packages.label)])
    statement = statement_for(seeds, options)
    built = materialiser.materialise(context, statement, dict(options or {}), lines)
    return loading.Built(armature=None, manifest=packages.manifest,
                         missing=list(built.missing) + list(packages.missing),
                         warnings=built.warnings, imported=built.imported)


def _role_layers():
    """The texture-role layers this install resolves its materials through: the
    layer of the module that claims this product, then the user's own."""
    import os

    from ... import Game
    from ...Kernel import host as host_port
    from ...Kernel.unity import texture_roles

    product = cabmap_state.active_game() or ""
    layers = []
    module = Game.module_for(product, "") if product else None
    if module is not None and getattr(module, "directory", ""):
        if (module.game_name or "").lower() == product.lower():
            path = os.path.join(module.directory, texture_roles.DEFAULT_LAYER_NAME)
            if os.path.isfile(path):
                layers.append(path)
    directory = host_port.current().preset_dir()
    if directory and product:
        user_layer = os.path.join(directory, "TextureRoles", product + ".json")
        if os.path.isfile(user_layer):
            layers.append(user_layer)
    return layers
