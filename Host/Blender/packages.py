"""Putting one resolved thing into the document.

The panel decides WHAT (a prefab, an assembly of parts, a scene window, a
performance); the reader says what that thing IS, as one statement; this puts the
statement into Blender. Nothing here opens a container or decodes a mesh: by the
time anything lands here the whole flattening has already happened once, on the
reader side, for every seed at once.

A seed is whatever the selection carries -- the container path the game files the
thing under, or the archive it lives in. Both are addresses the reader resolves
for any title, which is why no game is named in this module.
"""

from __future__ import annotations

import os

from ...Kernel import statement as kernel_statement
from ...Kernel.app import loading
from . import materialise as materialiser


def seeds_of(packages):
    """What to ask the reader about. Paths first: a path names one asset, while
    an archive names everything that shares it."""
    if getattr(packages, "seed", ""):
        return [packages.seed]
    paths = [path for path in (packages.paths or {}).values() if path]
    if paths:
        return sorted(set(paths))
    return [cab for cab in packages.cabs if cab]


def statement_for(context, seeds, options=None):
    """The statement these seeds make: this host's basis, this install's own
    texture-role layers, the options in front of the person.

    The options that CROSS are the ones that are questions about the selection --
    which detail level, whether switched-off renderers count. Everything else in
    the options table is about what this host then does with the answer."""
    from ...Kernel import host as host_port

    host = host_port.current()
    values = dict(options or {})
    arguments = {
        "detail": int(values.get("detail_level", 0) or 0),
        "inactive": bool(values.get("import_inactive", True)),
        "shadow_proxies": bool(values.get("import_shadow_proxies", False)),
        "containers": list(host.texture_containers() or ()),
        "roles": _role_layers(),
    }
    return kernel_statement.Statement.of(seeds, basis=_basis(host), **arguments)


def materialise(context, packages, resolved=None, options=None, report=None):
    """Bring one resolved thing into the scene.

    ``resolved`` is what the old closure pass produced and is no longer read: the
    statement covers everything it carried."""
    seeds = seeds_of(packages)
    if not seeds:
        return loading.Built(warnings=["{0} states nothing to load.".format(
            packages.label or packages.key or "That selection")])
    statement = statement_for(context, seeds, options)
    built = materialiser.materialise(context, statement, options or {}, report)
    return _as_report(built, packages)


def build_clips(context, clip_cab, clip_guids, database=None, options=None,
                display_names=None, activate=False, rig=None):
    """The performances one selection states, onto the rig they go on.

    The rig is the caller's where it knows one (a cast member's own armature in a
    batch) and whatever the host has selected otherwise. Curves arrive already
    anchored on that rig's own bone paths, with a muscle encoding solved against
    the avatar it carries, so there is no solver on this side."""
    from ...Kernel import host as host_port

    host = host_port.current()
    seeds = [name for name in ([clip_cab] if clip_cab else []) + list(clip_guids or ())
             if name]
    if not seeds:
        return 0
    target = host.selected_rig(context) if rig is None else rig
    if target is None:
        return 0
    statement = statement_for(context, seeds, options)
    paths = [entry["name"] for entry in host.rig_rest(context, target)]
    avatar = (host.rig_memory(target) or {}).get("avatar", "")
    clips = statement.clips(paths=paths, avatar=avatar)
    if not clips:
        return 0
    from . import animation_builder

    built, _lines = animation_builder.play(context, target, clips, dict(options or {}),
                                           activate)
    return built


def _as_report(built, packages):
    return loading.Built(armature=built.rig, manifest=packages.manifest,
                         missing=list(built.missing) + list(packages.missing),
                         warnings=built.warnings, imported=built.imported)


def _identity():
    """What the install in front of the panel published about itself: its own
    product name, and the engine family it runs on."""
    from ...Kernel.bridge import cabmap_state

    return cabmap_state.active_game() or "", ""


def _role_layers():
    """The texture-role layers this install resolves its materials through: the
    reader's own default underneath, then the layer of the MODULE that claims
    this product, then the user's own.

    Which folder a game's layer lives in is the module's fact, never the
    product's -- one module reads several titles, and two titles of one engine
    are two vocabularies."""
    from ... import Game
    from ...Kernel.unity import texture_roles

    product, engine = _identity()
    layers = []
    module = Game.module_for(product, engine) if product else None
    if module is not None and getattr(module, "directory", ""):
        # Only the module declared for THIS product owns a layer: a family module
        # that reads any title of an engine states nothing about one of them.
        if (module.game_name or "").lower() == (product or "").lower():
            path = os.path.join(module.directory, texture_roles.DEFAULT_LAYER_NAME)
            if os.path.isfile(path):
                layers.append(path)
    user_layer = _user_layer(product)
    if user_layer:
        layers.append(user_layer)
    return layers


def _user_layer(product):
    """What the user said the unnamed properties of THIS product are."""
    from ...Kernel import host as host_port

    directory = host_port.current().preset_dir()
    if not directory or not product:
        return ""
    path = os.path.join(directory, "TextureRoles", product + ".json")
    return path if os.path.isfile(path) else ""


def _basis(host):
    """The basis this host states geometry in, by NAME -- the reader converts."""
    return str(getattr(host, "BASIS", "") or "blender")
