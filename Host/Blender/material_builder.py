"""What a stated material becomes in this host, and the door a shader stack
plugs into.

Two things live here and they are one unit. The first is the DOOR: a generated
shader stack (``Game/<game>/shader/Blender/``) is a projection of a recipe, and
that projection names this module and these functions as the place it registers
itself. Which functions those are is DATA inside the product -- its manifest
carries ``registry_module``/``register_fn`` and the rest -- so the names here are
the product's statement about its host, not a choice made here. Behind each name
is one :class:`Kernel.extensions.ExtensionPoint`; there is no list in this file.

The second is the FALLBACK: a material no stack claims still has to be built,
and for an engine-standard shader the Principled BSDF IS the faithful build --
same physically-based model, and the roles the kernel resolved say which of the
material's own textures and numbers feed which input. Nothing here matches a
property by how its name looks: the vocabulary is the layered role table, merged
on the kernel side.
"""

from __future__ import annotations

import os

import bpy

from ...Kernel import extensions

#: A stack registers ``provider(builder, props) -> bpy.types.Material | None``
#: and SELF-SELECTS by the material's own shader identity, returning None to
#: decline. First claimant wins; no claimant lands on the fallback below.
GRAPH_PROVIDERS = extensions.point(
    "blender.graph_providers",
    "Node graphs a generated shader stack builds for the materials it claims.")

#: ``apply_vertex_stage(objects=None, camera=None) -> int``. Every stage only
#: touches materials and modifiers it owns, so running all of them is
#: order-independent. The ONE caller is the derived-state scheduler. This point
#: carries the TOPOLOGY half only -- the geometry tree and the modifier holding
#: it -- so it is reached only when something entered the scene.
VERTEX_STAGES = extensions.point(
    "blender.vertex_stages",
    "The vertex tree and its modifier a shading stack builds when assets arrive.")

#: ``push_camera_basis(objects=None, camera=None) -> int``. The camera basis,
#: the half FOV and the backbuffer size are UNIFORMS baked into the vertex tree
#: -- an outline is authored as a constant width in screen pixels, so they go
#: stale the moment the camera moves. What goes stale is the VALUE, not the
#: topology: a stage re-fills those sockets on trees that already exist and
#: never builds one.
#:
#: 拆出来的理由是行为不是性能:与建树合在一条上时,推一下镜头就等于按材质**现值**重判
#: 一次「这张材质该不该有描边」,于是用户手删掉的修改器会自己长回来,而画面上没有任何
#: 东西说明是谁加的。生成修改器只属于从游戏导入的那一刻。
CAMERA_STAGES = extensions.point(
    "blender.camera_stages",
    "Camera uniforms a shading stack re-fills on vertex trees that already exist.")

#: ``apply_rig_basis(objects=None) -> int``. The face basis is a per-object
#: uniform wired into the MATERIAL, never a geometry attribute, so
#: re-translating a bone identity into today's bone name touches no modifier at
#: all -- which is why it is its own point instead of a side effect of building
#: the vertex tree.
RIG_STAGES = extensions.point(
    "blender.rig_stages",
    "Re-translating a stack's bone identities into the rig's current bone names.")

#: ``rewire_capabilities(material) -> bool``. A shader's environment queries are
#: cut at the group interface and answered from scene state, so changing that
#: state leaves the answer stale until the fulfilment nodes are rebuilt. Only
#: those nodes, never the graph: a full rebuild would take the user's tuned
#: parameters back to shipped defaults.
CAPABILITY_REWIRES = extensions.point(
    "blender.capability_rewires",
    "Re-answering a built material's environment queries after the scene changed.")

#: ``refresh()``. Re-stamps WHICH LIGHT IS THE MAIN ONE -- a per-light custom
#: property the stack's own light loop reads. No texture stands in for lights, so
#: a light that moves costs the shading nothing.
LIGHT_ROLE_REFRESHERS = extensions.point(
    "blender.light_roles",
    "Re-picking the main light for each shading stack after the light set changed.")

#: A whole MODULE rather than one function: post-processing owns scene-level
#: state (the compositor tree, the view transform), so it has to be able to hand
#: that state back as well as take it -- install / uninstall / installed.
POST_STAGES = extensions.point(
    "blender.post_stages",
    "Whole-frame processing a shading stack installs onto the scene.")

#: ``level_global_bases() -> {name: [default, ...]}``. Engine globals a stack
#: reads LIVE from scene properties instead of baking them into its materials --
#: per-level values such as fog -- each with the default its recipe declares. The
#: stack's graph reads ``property + default``, so a property that was never
#: written answers the default and a session with no level in it is unchanged.
LEVEL_GLOBALS = extensions.point(
    "blender.level_globals",
    "Per-level engine globals a shading stack reads live from scene properties.")

#: ``level_image_layouts() -> {name: layout}``. The images a stack reads level
#: state through, since the host's material nodes only sample 2D images: 3D
#: textures and 2D texture arrays laid out as atlases, uniform struct arrays as
#: data tables. Per name, the image, its kind and size, how it is laid out and the
#: texel format -- plus, for a volume, the in-slice address modes that decide what
#: the ring around each slice holds.
LEVEL_IMAGES = extensions.point(
    "blender.level_images",
    "Images a shading stack reads level state through, which the host fills.")

#: Custom property stamped on every material this module or a stack builds.
SOURCE_KEY_PROPERTY = "ruri_source_key"
#: Marker on an image datablock: its colour space is already what the ASSET
#: declares, and nothing that infers one from a slot may overwrite it.
COLORSPACE_STATED_PROPERTY = "ruri_colorspace_stated"
#: Channel 3 of an RGBA map. Blender never colour-manages alpha, so a role that
#: reads only this channel puts no requirement on the image's colour space.
_ALPHA_CHANNEL = 3

_ORPHAN_FRAME_LABEL = "Unclaimed shader: {0}"
_CHANNEL_NAMES = ("R", "G", "B", "A")


# ---------------------------------------------------------------------------
# The door -- the names a generated product binds to
# ---------------------------------------------------------------------------
def register_graph_provider(provider):
    GRAPH_PROVIDERS.add(provider)


def unregister_graph_provider(provider):
    GRAPH_PROVIDERS.remove(provider)


def register_vertex_stage(stage):
    VERTEX_STAGES.add(stage)


def unregister_vertex_stage(stage):
    VERTEX_STAGES.remove(stage)


def register_camera_stage(stage):
    CAMERA_STAGES.add(stage)


def unregister_camera_stage(stage):
    CAMERA_STAGES.remove(stage)


def register_rig_stage(stage):
    RIG_STAGES.add(stage)


def unregister_rig_stage(stage):
    RIG_STAGES.remove(stage)


def register_capability_rewire(rewire):
    CAPABILITY_REWIRES.add(rewire)


def unregister_capability_rewire(rewire):
    CAPABILITY_REWIRES.remove(rewire)


def register_light_role_refresh(refresh):
    LIGHT_ROLE_REFRESHERS.add(refresh)


def unregister_light_role_refresh(refresh):
    LIGHT_ROLE_REFRESHERS.remove(refresh)


def register_post_stage(stage):
    POST_STAGES.add(stage)


def unregister_post_stage(stage):
    POST_STAGES.remove(stage)


def register_level_globals(bases):
    LEVEL_GLOBALS.add(bases)


def unregister_level_globals(bases):
    LEVEL_GLOBALS.remove(bases)


def register_volume_textures(layouts):
    """The door a stack hands its level-image layouts through (see LEVEL_IMAGES). Every
    deployed stack of every game binds this name, so it keeps it while the layouts it
    carries grew kinds beyond 3D textures."""
    LEVEL_IMAGES.add(layouts)


def unregister_volume_textures(layouts):
    LEVEL_IMAGES.remove(layouts)


def register_material_panel(panel):
    """A stack hands over its INTERFACE and its own read/write paths, not a panel:
    a session holds several stacks, and one panel each would stack N property
    pages beside each other while a person only ever wants the one the selected
    mesh is wearing. The host draws that single panel; this is the door the
    generated product can see."""
    from . import material_panel
    material_panel.register_stack(panel)


def unregister_material_panel(panel):
    from . import material_panel
    material_panel.unregister_stack(panel)


# ---------------------------------------------------------------------------
# What the derived-state scheduler runs
# ---------------------------------------------------------------------------
def apply_vertex_stages(objects=None, camera=None):
    return sum(stage(objects=objects, camera=camera) for stage in VERTEX_STAGES)


def push_camera_stages(objects=None, camera=None):
    return sum(stage(objects=objects, camera=camera) for stage in CAMERA_STAGES)


def apply_rig_stages(objects=None):
    return sum(stage(objects=objects) for stage in RIG_STAGES)


def rewire_capabilities(materials=None):
    """Re-answer the environment queries of every built material. A stack returns
    False for a material it did not build, so asking all of them is safe and
    order-independent. Returns how many were claimed and rewired."""
    pool = list(bpy.data.materials) if materials is None else list(materials)
    return sum(1 for material in pool
               if material is not None
               and any(rewire(material) for rewire in CAPABILITY_REWIRES))


def refresh_light_roles():
    """Re-stamp the main-light role. Unlike the rewire there is nothing
    per-material to count -- each stack re-picks ONE light -- so the report counts
    the refreshers that ran."""
    for refresh in LIGHT_ROLE_REFRESHERS:
        refresh()
    return len(LIGHT_ROLE_REFRESHERS)


def apply_post_stages(scene, force=False):
    """Install every registered post stage onto a scene.

    Already installed is skipped by default: install() rebuilds the whole
    compositor tree and writes the view transform and the viewport's compositor
    switch back to shipped values, so re-running it on every import silently
    zeroes every knob the user turned. ``force`` is the panel button that means
    start over.

    More than one stage would be two owners of one compositor tree, so that is
    reported rather than silently letting the last one win."""
    if len(POST_STAGES) > 1:
        print("[material] !! {0} post stages registered; a scene has ONE compositor "
              "tree, the last installed wins".format(len(POST_STAGES)))
    return [stage.install(scene) for stage in POST_STAGES
            if force or not stage.installed(scene)]


def remove_post_stages(scene):
    """Hand the scene back the compositor state it had before any stage was
    installed. Without this a load is one-way."""
    return [stage.uninstall(scene) for stage in POST_STAGES]


def post_stages_installed(scene):
    return [stage for stage in POST_STAGES if stage.installed(scene)]


def world_basis():
    """The source-world -> Blender-world basis every generated shading stack computes
    in, row-major (b = M @ u): the reflection plus the once-only top-level turn, off the
    one coordinate space the importer places everything with. A stack's kernel works in
    the SOURCE's world, not in each object's local frame -- the local frame is the world
    only for an object whose transform IS that turn, and a scene's placements each carry
    their own. The generator states the same matrix in its recipe (it builds templates
    with no plugin loaded); a stack checks it against this at registration."""
    from .coordinate import SPACE
    return (SPACE.root_rotation @ SPACE.matrix)[:3, :3].tolist()


def apply_post_inputs(scene, values):
    """Drive the host-side inputs of every post stage that declares any.

    ``values`` is keyed by the stage's own input names; each is the DIFFERENCE from
    identity, because an entry parameter's socket default is always zero and only a
    difference makes "nothing drives it" mean "no change" -- a session with a character
    and no scene has to land on identity.

    A stage whose inputs are not all supplied is refused rather than part-written: the
    missing one would silently fall back to identity and the picture would be quietly
    wrong with nothing to show for it.

    The inputs live on the installed stage, so a stage not installed yet is installed
    here first: an import states its grading before the derived-state pass would get
    round to installing the stage, and written into nothing the grading was lost."""
    written = 0
    for stage in POST_STAGES:
        names = stage.extra_inputs()
        if not names:
            continue
        missing = [name for name in names if name not in values]
        if missing:
            raise KeyError("[material] post stage wants {0}; {1} not supplied".format(
                names, missing))
        if not stage.installed(scene):
            stage.install(scene)
        written += stage.set_extra(scene, [values[name] for name in names])
    return written


def apply_level_resources(scene, values, payloads):
    """Apply everything one level states for every material: its engine globals and
    the texel blocks its stacks read (3D textures, texture arrays, data tables).

    ``values`` holds globals already in hand, keyed by the engine's own names;
    ``payloads`` are level-resources blobs (named globals plus named texel blocks, see
    :func:`_level_resources`). They are merged before anything is written -- the
    completeness rule below is about the level's whole state, and a level states it
    through more than one source (fog is static, the irradiance clipmaps and the
    reflection probes follow the camera). A name two sources both state with
    different values is refused.

    Returns ``(written, unclaimed)``: the names written, and the supplied names no
    registered stack reads."""
    merged = {name: tuple(value) for name, value in values.items()}
    blocks = {}
    for payload in payloads:
        stated_globals, stated_blocks = _level_resources(payload)
        for name, value in stated_globals.items():
            if name in merged and merged[name] != value:
                raise ValueError("[material] level global {0} stated twice: {1} and {2}".format(
                    name, merged[name], value))
            merged[name] = value
        for name, block in stated_blocks.items():
            if name in blocks:
                raise ValueError("[material] level block {0} stated twice".format(name))
            blocks[name] = block
    written, unclaimed = _apply_level_globals(scene, merged)
    filled, unread = _apply_level_images(blocks)
    return written + filled, unclaimed + unread


def _apply_level_globals(scene, values):
    """Write one level's engine globals where the stacks read them live.

    ``values`` is keyed by the engine's own global names, each the level's value in
    the source's own convention. What lands on the scene is the DIFFERENCE from the
    stack's declared default, because the graph reads ``property + default`` and an
    unwritten property reads zero.

    A stack that is handed some of its level globals but not all is refused: the
    missing ones would silently stay at the recipe default and the picture would be
    quietly wrong. A stack handed none of them is not this level's consumer (another
    game's stack) and is left alone. Two stacks declaring different defaults for one
    name cannot share a scene property, so that is refused too."""
    bases = {}
    for provider in LEVEL_GLOBALS:
        declared = provider()
        supplied = [name for name in declared if name in values]
        if supplied and len(supplied) != len(declared):
            raise KeyError("[material] a stack reads level globals {0}; {1} not supplied".format(
                sorted(declared), sorted(name for name in declared if name not in values)))
        for name, base in declared.items():
            known = bases.setdefault(name, list(base))
            if known != list(base):
                raise ValueError("[material] level global {0} has two defaults: {1} and {2}".format(
                    name, known, list(base)))
    written = []
    for name, value in values.items():
        base = bases.get(name)
        if base is None:
            continue
        if len(value) != len(base):
            raise ValueError("[material] level global {0} has {1} components, the stack reads {2}".format(
                name, len(value), len(base)))
        scene[name] = [float(component) - component_base for component, component_base in zip(value, base)]
        written.append(name)
    scene.update_tag()
    return written, sorted(name for name in values if name not in bases)


_LEVEL_RESOURCES_MAGIC = 0x52564C52
_LEVEL_RESOURCES_VERSION = 2
_TEXEL_FORMATS = {1: "<f2", 2: "u1", 3: "<f4"}
_BLOCK_KINDS = {0: "volume", 1: "array"}


def _level_resources(payload):
    """``(globals, blocks)`` from one level-resources blob: little-endian ``"RLVR",
    version``, then named four-component globals, then named texel blocks -- a kind
    byte (0 = 3D texture, 1 = 2D texture array), ``width, height, depth, mips,
    channels``, a format byte (1 = half, 2 = unorm8, 3 = float) and the texels of every
    mip from the largest, each x fastest, then y, then z. A mip halves a volume's depth
    with its width and height and keeps an array's slice count; a uniform array of
    four-component rows is a one-slice array.

    A block comes back as ``(kind, levels)``: one float32 array per mip shaped (depth,
    height, width, channels), unorm8 already divided by 255."""
    import struct
    import numpy
    view = memoryview(payload)
    magic, version = struct.unpack_from("<II", view, 0)
    if magic != _LEVEL_RESOURCES_MAGIC:
        raise ValueError("[material] not a level-resources payload")
    if version != _LEVEL_RESOURCES_VERSION:
        raise ValueError("[material] level-resources version {0}; this host reads {1}".format(
            version, _LEVEL_RESOURCES_VERSION))
    cursor = 8

    def name():
        nonlocal cursor
        length = struct.unpack_from("<H", view, cursor)[0]
        text = bytes(view[cursor + 2:cursor + 2 + length]).decode("utf-8")
        cursor += 2 + length
        return text

    stated_globals = {}
    count = struct.unpack_from("<i", view, cursor)[0]
    cursor += 4
    for _ in range(count):
        key = name()
        stated_globals[key] = struct.unpack_from("<4f", view, cursor)
        cursor += 16
    blocks = {}
    count = struct.unpack_from("<i", view, cursor)[0]
    cursor += 4
    for _ in range(count):
        key = name()
        kind = _BLOCK_KINDS[view[cursor]]
        width, height, depth, mips, channels = struct.unpack_from("<5i", view, cursor + 1)
        texel_format = _TEXEL_FORMATS[view[cursor + 21]]
        cursor += 22
        levels = []
        for mip in range(mips):
            level_width, level_height = max(1, width >> mip), max(1, height >> mip)
            level_depth = max(1, depth >> mip) if kind == "volume" else depth
            total = level_width * level_height * level_depth * channels
            texels = numpy.frombuffer(view, dtype=texel_format, count=total, offset=cursor)
            cursor += texels.nbytes
            texels = texels.astype(numpy.float32)
            if texel_format == "u1":
                texels /= 255.0
            levels.append(texels.reshape(level_depth, level_height, level_width, channels))
        blocks[key] = (kind, levels)
    if cursor != len(view):
        raise ValueError("[material] level-resources payload has {0} trailing bytes".format(len(view) - cursor))
    return stated_globals, blocks


def volume_image(layout):
    """The one image a stack reads a level resource through, laid out as ``layout``
    says (a generated product's level-image row). The only place such an image is
    made: a stack asks for it when it builds a template, the level writes into it.
    A size that no longer matches is rebuilt -- the stack's coordinates are the
    layout's constants, and sampling another size would shift every tile.

    Every channel is data, the fourth included (the irradiance clipmaps keep sky
    visibility there), so the alpha is channel-packed: read as straight alpha, the
    colour channels are premultiplied on upload and come back zero wherever the
    fourth channel is. A data table holds the single-precision values the source
    reads as they are (positions, matrix rows), so it goes to the GPU at full
    precision; the atlases hold half and 8-bit texels and keep the half upload."""
    size = layout["size"] if layout["kind"] == "table" else layout["atlas"]
    width, height = (int(value) for value in size)
    image = bpy.data.images.get(layout["image"])
    if image is not None and (int(image.size[0]), int(image.size[1])) != (width, height):
        bpy.data.images.remove(image)
        image = None
    if image is None:
        float_buffer = layout["format"] in ("HALF", "FLOAT")
        image = bpy.data.images.new(layout["image"], width, height, alpha=True, float_buffer=float_buffer)
        image.colorspace_settings.name = "Non-Color"
        image.file_format = "OPEN_EXR" if float_buffer else "PNG"
    if image.alpha_mode != "CHANNEL_PACKED":
        image.alpha_mode = "CHANNEL_PACKED"
    full_precision = layout["format"] == "FLOAT"
    if image.use_half_precision == full_precision:
        image.use_half_precision = not full_precision
    return image


def _address(index, count, mode):
    """One texel index under a sampler address mode (the same rule the stacks lower)."""
    if mode == "WRAP":
        return index % count
    if mode == "MIRROR":
        period = index % (2 * count)
        return period if period < count else 2 * count - 1 - period
    if mode == "MIRRORONCE":
        folded = -index - 1 if index < 0 else index
        return min(folded, count - 1)
    return min(max(index, 0), count - 1)


def _volume_pixels(levels, layout):
    """A 3D texture (one mip) laid out as the stack reads it: slice z at grid cell
    (z % columns, z // columns), row 0 at the bottom (Blender's own pixel order), each
    cell ringed by ``pad`` texels holding the neighbours the stack's in-slice address
    mode would reach."""
    import numpy
    if len(levels) != 1:
        raise ValueError("[material] volume {0}: {1} mips stated, the atlas holds one".format(
            layout["image"], len(levels)))
    texels = levels[0]
    width, height, depth = (int(value) for value in layout["size"])
    if texels.shape[:3] != (depth, height, width):
        raise ValueError("[material] volume {0}: texels {1} against a {2}x{3}x{4} layout".format(
            layout["image"], texels.shape, width, height, depth))
    columns, pad = int(layout["columns"]), int(layout["pad"])
    atlas_width, atlas_height = (int(value) for value in layout["atlas"])
    mode_u, mode_v = layout["address"]
    xs = [_address(i, width, mode_u) for i in range(-pad, width + pad)]
    ys = [_address(j, height, mode_v) for j in range(-pad, height + pad)]
    ringed = texels[:, ys][:, :, xs]
    channels = texels.shape[3]
    pixels = numpy.zeros((atlas_height, atlas_width, 4), dtype=numpy.float32)
    tile_width, tile_height = width + 2 * pad, height + 2 * pad
    for z in range(depth):
        row, column = divmod(z, columns)
        pixels[row * tile_height:(row + 1) * tile_height,
               column * tile_width:(column + 1) * tile_width, :channels] = ringed[z]
    return pixels


def _array_pixels(levels, layout):
    """A 2D texture array with its mips laid out as the stack reads it: slice s in the
    tile at (s % columns, s // columns), row 0 at the bottom; inside a tile mip 0 sits
    at the tile's origin and mip m >= 1 at (width, height - 2 * (height >> m)), each at
    its own resolution with its first stored row at the bottom. Slices past the ones
    stated stay zero."""
    import numpy
    width, height = (int(value) for value in layout["size"])
    slices, mips, columns = int(layout["slices"]), int(layout["mips"]), int(layout["columns"])
    tile_width, tile_height = (int(value) for value in layout["tile"])
    atlas_width, atlas_height = (int(value) for value in layout["atlas"])
    if len(levels) != mips:
        raise ValueError("[material] array {0}: {1} mips stated, the atlas holds {2}".format(
            layout["image"], len(levels), mips))
    stated = levels[0].shape[0]
    if stated > slices:
        raise ValueError("[material] array {0}: {1} slices stated, the atlas holds {2}".format(
            layout["image"], stated, slices))
    pixels = numpy.zeros((atlas_height, atlas_width, 4), dtype=numpy.float32)
    for mip, texels in enumerate(levels):
        level_width, level_height = width >> mip, height >> mip
        if texels.shape[:3] != (stated, level_height, level_width):
            raise ValueError("[material] array {0}: mip {1} is {2}, the layout says {3}x{4}x{5}".format(
                layout["image"], mip, texels.shape[:3], level_width, level_height, stated))
        origin_x = width if mip > 0 else 0
        origin_y = height - 2 * level_height if mip > 0 else 0
        channels = texels.shape[3]
        for index in range(stated):
            row, column = divmod(index, columns)
            x = column * tile_width + origin_x
            y = row * tile_height + origin_y
            pixels[y:y + level_height, x:x + level_width, :channels] = texels[index]
    return pixels


def _table_pixels(levels, layout):
    """A uniform struct array as the stack reads it: element i on row i from the
    bottom, its four-component fields left to right."""
    import numpy
    fields, length = (int(value) for value in layout["size"])
    if len(levels) != 1 or levels[0].shape != (1, length, fields, 4):
        raise ValueError("[material] table {0}: stated {1}, the layout says {2} rows of {3} vectors".format(
            layout["image"], [level.shape for level in levels], length, fields))
    return numpy.ascontiguousarray(levels[0][0], dtype=numpy.float32)


_LEVEL_PIXELS = {"volume": _volume_pixels, "array": _array_pixels, "table": _table_pixels}


def _apply_level_images(blocks):
    """Fill the image behind every stated block some registered stack reads. Two
    stacks laying one resource out differently cannot share its image, so that is
    refused. Returns ``(filled, unread)``."""
    layouts = {}
    for provider in LEVEL_IMAGES:
        for name, layout in provider().items():
            known = layouts.setdefault(name, layout)
            if known != layout:
                raise ValueError("[material] level image {0} has two layouts".format(name))
    filled = []
    for name, (kind, levels) in blocks.items():
        layout = layouts.get(name)
        if layout is None:
            continue
        expected = "volume" if layout["kind"] == "volume" else "array"
        if kind != expected:
            raise ValueError("[material] level image {0}: stated as a {1}, read as a {2}".format(
                name, kind, layout["kind"]))
        image = volume_image(layout)
        image.pixels.foreach_set(_LEVEL_PIXELS[layout["kind"]](levels, layout).ravel())
        image.pack()
        filled.append(name)
    return filled, sorted(name for name in blocks if name not in layouts)


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def _image_from_bytes(data, name, extension=None):
    """Load a stated texture's bytes through Blender's OWN image loader, via a
    throwaway temp file -- measured pixel-identical to decoding them in python
    and 30x faster.

    The image is PACKED into the file and the temp deleted, so nothing on disk
    outlives the call. A content-addressed cache directory instead traded away
    both things a texture has to keep: IDENTITY (the file referenced a hash where
    the game says a name) and PORTABILITY (a document whose textures live in a
    machine-local folder cannot be moved, handed over or archived).

    The name is stamped in three places because they are three different records:
    the datablock name (what the UI lists), ``filepath_raw`` (what a relink
    resolves) and the PACKED FILE's own path (what File > Unpack writes). Unpack
    reads the last of those, which is why setting only the first two used to
    leave every unpacked texture called tmpXXXXXXXX.img."""
    import tempfile

    temp = tempfile.NamedTemporaryFile(suffix=".img", delete=False)
    try:
        temp.write(data)
        temp.close()
        try:
            image = bpy.data.images.load(temp.name)
        except RuntimeError:
            return None
        image.name = name
        target = "//textures/" + name + (extension or _image_extension(image))
        # Pack FIRST -- it reads the file while it is still on disk -- and only
        # then rewrite both path records to the game's own name.
        image.pack()
        if image.packed_files:
            image.packed_files[0].filepath = target
        image.filepath_raw = target
    finally:
        os.unlink(temp.name)
    _disable_alpha_interpretation(image)
    return image


#: Extension per image FORMAT, not per image: see _image_extension.
_EXTENSION_BY_FORMAT = {}


def _image_extension(image):
    """The extension Blender itself uses for this image's DETECTED format, read
    out of Blender's own format table rather than a map here -- a container this
    importer has never seen still unpacks under a truthful name.

    Asked ONCE PER FORMAT. Reading that table means writing the scene's render
    settings twice, and a scene write runs Blender's update machinery: measured
    27ms per call and 4.5s over one level's 164 textures, for an answer that
    depends on nothing but the format string."""
    detected = image.file_format or ""
    remembered = _EXTENSION_BY_FORMAT.get(detected)
    if remembered is None:
        _EXTENSION_BY_FORMAT[detected] = remembered = _read_image_extension(image, detected)
    return remembered


def _read_image_extension(image, detected):
    fallback = "." + (detected or "img").lower()
    render = getattr(getattr(bpy.context, "scene", None), "render", None)
    if render is None:
        return fallback
    previous = render.image_settings.file_format
    try:
        render.image_settings.file_format = image.file_format
        return render.file_extension or fallback
    except (TypeError, ValueError):
        # Blender can READ formats it cannot render to; those have no entry.
        return fallback
    finally:
        render.image_settings.file_format = previous


def _disable_alpha_interpretation(image):
    """These shaders routinely repurpose a texture's fourth channel for something
    other than opacity (ambient occlusion, an emission mask, a packed channel).
    Blender's default treats it as real transparency regardless of whether the
    graph ever wires the Alpha output anywhere, which reads as an incorrectly
    see-through material."""
    try:
        image.alpha_mode = "NONE"
    except Exception:
        pass


def _enable_alpha_channel(image):
    """Give an image back its alpha, for the one case that asks for it: a
    material that WIRES that channel as opacity is the material saying it IS
    opacity there. While the interpretation is off the Alpha output reads 1.0
    everywhere, so a cutout keeps the whole card."""
    try:
        image.alpha_mode = "CHANNEL_PACKED"
    except Exception:
        pass


# ---------------------------------------------------------------------------
# The builder
# ---------------------------------------------------------------------------
class MaterialBuilder:
    """Builds the materials of one statement, once each.

    A generated stack is handed this object and the stated material; the two
    names it reaches for -- ``options`` and ``_load_image`` -- are what its own
    manifest says its host provides."""

    def __init__(self, statement, options):
        self.statement = statement
        self.options = dict(options or {})
        self._by_key = {}
        self._images = {}

    def shader_display_name(self, props):
        """The shader a material names, as the shader asset calls itself. A stack
        claims by this and a report prints it."""
        return props.shader_name or None

    def build(self, key):
        """The Blender material for one stated material key, built once."""
        if key in self._by_key:
            return self._by_key[key]
        stated = self.statement.materials.get(key)
        if stated is None:
            made = bpy.data.materials.new(key or "Material")
            self._by_key[key] = made
            _announce(made)
            return made
        made = self._build(stated)
        made[SOURCE_KEY_PROPERTY] = str(key)
        self._by_key[key] = made
        _announce(made)
        return made

    def _load_image(self, guid, non_color=False):
        """The image behind one texture key, loaded once.

        Named ``_load_image`` because that is the name a generated product's
        manifest states for it; the key is called a guid for the same reason."""
        if not guid:
            return None
        cached = self._images.get(guid)
        if cached is None:
            texture = self.statement.textures.get(guid)
            if texture is None or not texture.bytes:
                return None
            cached = _image_from_bytes(texture.image, texture.name or guid,
                                       "." + texture.container if texture.container else None)
            if cached is None:
                return None
            self._images[guid] = cached
        # Colour space is the TEXTURE's own fact, never the slot's: one image is
        # routinely bound in a normal slot and an emission slot at once, and the
        # setting lives on the shared datablock where the last writer wins. Only
        # what the asset itself declares is honoured, and it is marked so nothing
        # downstream re-infers one from a slot.
        texture = self.statement.textures.get(guid)
        want = None
        if texture is not None:
            want = "sRGB" if texture.srgb else "Non-Color"
            cached[COLORSPACE_STATED_PROPERTY] = True
        elif non_color:
            want = "Non-Color"
        if want is not None and cached.colorspace_settings.name != want:
            try:
                cached.colorspace_settings.name = want
            except Exception:
                pass
        return cached

    def _build(self, props):
        name = props.name or "Material"
        # Generated stacks first, each declining with None. Every material is
        # asked, engine-standard ones included -- they simply resolve to a name
        # no stack claims, which is the intended route rather than a gap: the
        # Principled fallback below IS the faithful build for a standard shader.
        if self.options.get("game_shaders"):
            for provider in GRAPH_PROVIDERS:
                try:
                    claimed = provider(self, props)
                except Exception:
                    import traceback
                    traceback.print_exc()
                    print("[material] !! provider {0} EXCEPTION on '{1}' -- falling back "
                          "to Principled, the graph is NOT the game shader".format(
                              getattr(provider, "__module__", provider), name))
                    claimed = None
                if claimed is not None:
                    return claimed
            print("[material] UNCLAIMED '{0}' shader={1} -- Principled fallback".format(
                name, props.shader_name or "<none>"))
        return self._principled(props)

    def _principled(self, props):
        roles = props.roles
        # Rewrite a same-named material in place: a mesh binds its material by
        # name, and a second datablock would take a .001 suffix and leave two.
        material = bpy.data.materials.get(name_of(props)) or bpy.data.materials.new(name_of(props))
        material.use_nodes = True
        tree = material.node_tree
        tree.nodes.clear()
        output = tree.nodes.new("ShaderNodeOutputMaterial")
        output.location = (600, 0)
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (200, 0)
        tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
        claimed = set()

        base_node = self._wire_base_colour(tree, bsdf, roles, claimed)
        self._wire_opacity(material, tree, bsdf, roles, base_node)
        self._wire_normal(tree, bsdf, roles, claimed)
        self._wire_scalars(tree, bsdf, roles, claimed)
        self._wire_emission(tree, bsdf, roles, claimed)
        _orphan_textures(self, tree, props, claimed)
        return material

    def _wire_base_colour(self, tree, bsdf, roles, claimed):
        """The material's own tint MULTIPLIES the texture exactly as these
        shaders do; a neutral white tint adds no node."""
        tint = roles.colors.get("base_color")
        base = roles.first("base_color")
        if base is None:
            if tint is not None:
                bsdf.inputs["Base Color"].default_value = tuple(tint)
            return None
        claimed.add(base.name)
        image = self._load_image(base.guid)
        if image is None:
            return None
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = image
        node.location = (-400, 100)
        node.label = base.name
        socket = node.outputs["Color"]
        if tint is not None and tuple(tint[:3]) != (1.0, 1.0, 1.0):
            mix = tree.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.clamp_factor = False
            mix.location = (-100, 100)
            mix.inputs["Factor"].default_value = 1.0
            tree.links.new(socket, mix.inputs["A"])
            mix.inputs["B"].default_value = (float(tint[0]), float(tint[1]), float(tint[2]), 1.0)
            socket = mix.outputs["Result"]
        tree.links.new(socket, bsdf.inputs["Base Color"])
        return node

    def _wire_opacity(self, material, tree, bsdf, roles, base_node):
        """The blend state is material DATA when the material declares one.

        An opaque material routinely repurposes the base map's alpha, so wiring
        it as opacity turns whole walls translucent -- honour the declared mode.
        And an alpha TEST is not alpha blending: a material stating a cutoff asks
        for every texel to be all there or not there at all, and handing its soft
        alpha to a stochastic blend loses most of it to dithering noise."""
        mode = roles.floats.get("blend_mode")
        wire = True if mode is None else float(mode) >= 0.5
        opacity_texture, opacity_channel = roles.with_channel("opacity")
        base = roles.first("base_color")
        if opacity_texture is not None and opacity_texture is base and opacity_channel == _ALPHA_CHANNEL:
            wire = True
        if base_node is not None and wire:
            cutoff = roles.floats.get("alpha_cutoff")
            _enable_alpha_channel(base_node.image)
            socket = base_node.outputs["Alpha"]
            if cutoff is not None and float(cutoff) > 0.0:
                test = tree.nodes.new("ShaderNodeMath")
                test.operation = "GREATER_THAN"
                test.location = (-100, -150)
                test.label = "alpha cutoff {0:.3f}".format(float(cutoff))
                test.inputs[1].default_value = float(cutoff)
                tree.links.new(socket, test.inputs[0])
                socket = test.outputs["Value"]
            tree.links.new(socket, bsdf.inputs["Alpha"])
        if mode is not None:
            try:
                material.surface_render_method = "BLENDED" if float(mode) >= 1.5 else "DITHERED"
            except Exception:
                pass

    def _wire_normal(self, tree, bsdf, roles, claimed):
        normal = roles.first("normal")
        if normal is None:
            return
        claimed.add(normal.name)
        strength = float(roles.floats.get("normal_strength", 1.0) or 1.0)
        image = self._load_image(normal.guid, non_color=True)
        if image is None:
            return
        if normal.encoding == "hair_split":
            _wire_hair_split_normal(tree, bsdf, image, strength, (-400, -250))
            return
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = image
        node.location = (-400, -250)
        node.label = normal.name
        mapping = tree.nodes.new("ShaderNodeNormalMap")
        mapping.location = (-100, -250)
        mapping.inputs["Strength"].default_value = strength
        tree.links.new(node.outputs["Color"], mapping.inputs["Color"])
        tree.links.new(mapping.outputs["Normal"], bsdf.inputs["Normal"])

    def _wire_scalars(self, tree, bsdf, roles, claimed):
        """Every texture the layers give a channel role to, each on its own
        separator; the first to state metallic or roughness feeds the BSDF. With
        no packed map, the material's own numbers ARE the truth."""
        metallic_wired = False
        roughness_wired = False
        for index, packed in enumerate(roles.packed()):
            claimed.add(packed.name)
            # ALPHA IS NOT COLOUR MANAGED. Reading channel 3 says nothing about
            # how the RGB is to be read, so a map used only for its alpha must
            # not drag the image to Non-Color: it is routinely the SAME picture
            # as the base colour (one title states the diffuse under two names in
            # 1500 of 1663 measured materials), the setting lives on the shared
            # datablock, and the last writer wins -- so the whole game renders
            # dark with nothing anywhere to show for it.
            reads_colour = any(channel != _ALPHA_CHANNEL
                               for channel in packed.channels.values())
            image = self._load_image(packed.guid, non_color=reads_colour)
            if image is None:
                continue
            channels = dict(packed.channels)
            if metallic_wired:
                channels.pop("metallic", None)
            if roughness_wired:
                channels.pop("roughness", None)
                channels.pop("smoothness", None)
            got_metallic, got_roughness = _wire_packed(
                tree, bsdf, image, packed.name, channels, (-400, -420 - index * 320))
            metallic_wired = metallic_wired or got_metallic
            roughness_wired = roughness_wired or got_roughness
        if not metallic_wired and roles.floats.get("metallic") is not None:
            bsdf.inputs["Metallic"].default_value = float(roles.floats.get("metallic"))
        if roughness_wired:
            return
        if roles.floats.get("roughness") is not None:
            bsdf.inputs["Roughness"].default_value = float(roles.floats.get("roughness"))
        elif roles.floats.get("smoothness") is not None:
            bsdf.inputs["Roughness"].default_value = 1.0 - float(roles.floats.get("smoothness"))

    def _wire_emission(self, tree, bsdf, roles, claimed):
        """Emission is the map times its colour factor: a BLACK emission colour
        means emission OFF even with a map bound, and skipping the multiply made
        every such material glow at full map brightness. A colour alone, when it
        is not black, is emission with no map."""
        emission = roles.first("emission")
        colour = roles.colors.get("emission")
        if "Emission Color" not in bsdf.inputs:
            return
        if emission is not None:
            claimed.add(emission.name)
            image = self._load_image(emission.guid)
            if image is None:
                return
            node = tree.nodes.new("ShaderNodeTexImage")
            node.image = image
            node.location = (-400, -750)
            node.label = emission.name
            socket = node.outputs["Color"]
            if colour is not None and tuple(colour[:3]) != (1.0, 1.0, 1.0):
                mix = tree.nodes.new("ShaderNodeMix")
                mix.data_type = "RGBA"
                mix.blend_type = "MULTIPLY"
                mix.clamp_factor = False
                mix.location = (-100, -750)
                mix.inputs["Factor"].default_value = 1.0
                tree.links.new(socket, mix.inputs["A"])
                mix.inputs["B"].default_value = (float(colour[0]), float(colour[1]),
                                                 float(colour[2]), 1.0)
                socket = mix.outputs["Result"]
            tree.links.new(socket, bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = 1.0
            return
        if colour is not None and tuple(colour[:3]) != (0.0, 0.0, 0.0):
            bsdf.inputs["Emission Color"].default_value = (
                float(colour[0]), float(colour[1]), float(colour[2]), 1.0)
            bsdf.inputs["Emission Strength"].default_value = 1.0


def name_of(props):
    return props.name or "Material"


def _announce(*datablocks):
    """Tell the derived-state scheduler these datablocks just arrived. Imported
    inside the call: that module reads this one's points, and a module-level
    cycle would hand whichever loaded first a half-built other."""
    from . import derived_state
    derived_state.announce(*datablocks)


def _orphan_textures(builder, tree, props, claimed, origin=(-1100, 400)):
    """Put EVERY texture the material carries that nothing above claimed into the
    graph as an unconnected image node, inside a frame labelled with the shader.

    A shader's property names are whatever its author typed, and there is no rule
    that finds them all. Dropping the rest silently leaves a material that looks
    fully built while most of its content is missing, and the only clue -- the
    shader's name -- is a console line long since scrolled away. So they land as
    islands: the frame says which shader this was, each node is labelled with the
    property name the game gave it, and nothing is connected, because guessing a
    connection is how a normal map ends up in Base Color."""
    frame = tree.nodes.new("NodeFrame")
    frame.label = _ORPHAN_FRAME_LABEL.format(props.shader_name or "<none stated>")
    frame.shrink = True
    # An image a claimed slot already placed is not an orphan under another name:
    # a converter that states a slot's part beside the slot's own name gives the
    # same image two keys on purpose.
    claimed_keys = {props.textures.get(name) for name in claimed if name}
    left = [(name, key) for name, key in sorted(props.textures.items())
            if key and name not in claimed and key not in claimed_keys]
    for index, (name, key) in enumerate(left):
        image = builder._load_image(key)
        if image is None:
            continue
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = image
        node.label = name
        node.parent = frame
        node.location = (origin[0], origin[1] - index * 300)


def _wire_packed(tree, bsdf, image, label, channels, location):
    """A texture whose channels carry scalar roles: metallic and roughness go
    straight to the BSDF, smoothness through 1 - x; occlusion, specular, opacity
    and height have no Principled socket and stay on the sheet, the node labelled
    with what they are."""
    x, y = location
    node = tree.nodes.new("ShaderNodeTexImage")
    node.image = image
    node.location = (x, y)
    node.label = "{0}: {1}".format(label, ", ".join(
        "{0}={1}".format(role, _CHANNEL_NAMES[channel])
        for role, channel in sorted(channels.items()) if 0 <= channel < 4))
    separate = tree.nodes.new("ShaderNodeSeparateColor")
    separate.location = (x + 300, y)
    tree.links.new(node.outputs["Color"], separate.inputs["Color"])
    if _ALPHA_CHANNEL in channels.values():
        _enable_alpha_channel(image)
    outputs = {0: separate.outputs["Red"], 1: separate.outputs["Green"],
               2: separate.outputs["Blue"], 3: node.outputs["Alpha"]}
    metallic = channels.get("metallic")
    if metallic in outputs:
        tree.links.new(outputs[metallic], bsdf.inputs["Metallic"])
    roughness = channels.get("roughness")
    smoothness = channels.get("smoothness")
    if roughness in outputs:
        tree.links.new(outputs[roughness], bsdf.inputs["Roughness"])
    elif smoothness in outputs:
        invert = tree.nodes.new("ShaderNodeMath")
        invert.operation = "SUBTRACT"
        invert.inputs[0].default_value = 1.0
        invert.location = (x + 300, y - 180)
        tree.links.new(outputs[smoothness], invert.inputs[1])
        tree.links.new(invert.outputs["Value"], bsdf.inputs["Roughness"])
    return "metallic" in channels, "roughness" in channels or "smoothness" in channels


def _wire_hair_split_normal(tree, bsdf, image, bump_scale, location):
    """A split normal map that is NOT a standard two-channel normal map --
    ground-truthed instruction-by-instruction against the real compiled shader::

        _491 = R*2-1 ;  _493 = G*2-1                   (no alpha multiply: the
                                                        alpha here is the SPEC
                                                        normal's Y)
        _501 = max(sqrt(1 - min(dot(xy,xy), 1)), 1e-16) <- from the UNSCALED xy
        _507 = _491 * scale ;  _508 = _493 * scale      <- scale hits xy only
        N = normalize(_501*normal + _507*tangent + _508*bitangent)

    The hemisphere reconstruction uses the UNSCALED x/y and the scale is applied
    afterwards -- the same order the skin, fur and effect shaders use, with no
    per-part difference. Reconstructing Z from the SCALED x/y collapses Z to ~0
    once the scale exceeds 1, because 1 - scaled^2 goes negative and clamps; the
    two orders agree only at scale == 1, which is why it went unnoticed.

    B and A pack a SEPARATE specular-highlight normal, left unwired: the
    Principled BSDF has exactly one Normal input shared by diffuse and specular,
    and routing a genuinely different specular normal would need a fully custom
    anisotropic graph rather than a property-linking pass.

    Built from raw maths nodes, then fed back through a Normal Map node purely to
    reuse Blender's own tangent-space transform -- there is no node that accepts
    an already-tangent-space vector -- so the decoded vector is re-encoded to
    0..1 first and that node's own decode reconstructs exactly it."""
    x, y = location
    texture = tree.nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.location = (x, y)
    texture.label = "Split normal (RG diffuse, BA specular, specular unused)"

    separate = tree.nodes.new("ShaderNodeSeparateColor")
    separate.location = (x + 260, y)
    tree.links.new(texture.outputs["Color"], separate.inputs["Color"])

    raw = tree.nodes.new("ShaderNodeCombineXYZ")
    raw.location = (x + 460, y)
    tree.links.new(separate.outputs["Red"], raw.inputs["X"])
    tree.links.new(separate.outputs["Green"], raw.inputs["Y"])

    unit = tree.nodes.new("ShaderNodeVectorMath")
    unit.operation = "MULTIPLY_ADD"
    unit.location = (x + 660, y)
    unit.inputs[1].default_value = (2.0, 2.0, 0.0)
    unit.inputs[2].default_value = (-1.0, -1.0, 0.0)
    tree.links.new(raw.outputs["Vector"], unit.inputs[0])

    scaled = tree.nodes.new("ShaderNodeVectorMath")
    scaled.operation = "SCALE"
    scaled.location = (x + 860, y)
    scaled.inputs["Scale"].default_value = bump_scale
    tree.links.new(unit.outputs["Vector"], scaled.inputs[0])

    # The dot product is over the UNSCALED xy. Z is 0 in that vector, so a self
    # dot product is exactly x*x + y*y.
    squared = tree.nodes.new("ShaderNodeVectorMath")
    squared.operation = "DOT_PRODUCT"
    squared.location = (x + 1060, y)
    tree.links.new(unit.outputs["Vector"], squared.inputs[0])
    tree.links.new(unit.outputs["Vector"], squared.inputs[1])

    capped = tree.nodes.new("ShaderNodeMath")
    capped.operation = "MINIMUM"
    capped.location = (x + 1160, y)
    capped.inputs[1].default_value = 1.0
    tree.links.new(squared.outputs["Value"], capped.inputs[0])

    remainder = tree.nodes.new("ShaderNodeMath")
    remainder.operation = "SUBTRACT"
    remainder.location = (x + 1260, y)
    remainder.inputs[0].default_value = 1.0
    tree.links.new(capped.outputs["Value"], remainder.inputs[1])

    floored = tree.nodes.new("ShaderNodeMath")
    floored.operation = "MAXIMUM"
    floored.location = (x + 1420, y)
    floored.inputs[1].default_value = 1e-4
    tree.links.new(remainder.outputs["Value"], floored.inputs[0])

    depth = tree.nodes.new("ShaderNodeMath")
    depth.operation = "SQRT"
    depth.location = (x + 1580, y)
    tree.links.new(floored.outputs["Value"], depth.inputs[0])

    depth_vector = tree.nodes.new("ShaderNodeCombineXYZ")
    depth_vector.location = (x + 1580, y - 160)
    tree.links.new(depth.outputs["Value"], depth_vector.inputs["Z"])

    whole = tree.nodes.new("ShaderNodeVectorMath")
    whole.operation = "ADD"
    whole.location = (x + 1780, y)
    tree.links.new(scaled.outputs["Vector"], whole.inputs[0])
    tree.links.new(depth_vector.outputs["Vector"], whole.inputs[1])

    encoded = tree.nodes.new("ShaderNodeVectorMath")
    encoded.operation = "MULTIPLY_ADD"
    encoded.location = (x + 1980, y)
    encoded.inputs[1].default_value = (0.5, 0.5, 0.5)
    encoded.inputs[2].default_value = (0.5, 0.5, 0.5)
    tree.links.new(whole.outputs["Vector"], encoded.inputs[0])

    mapping = tree.nodes.new("ShaderNodeNormalMap")
    mapping.location = (x + 2180, y)
    mapping.inputs["Strength"].default_value = 1.0
    tree.links.new(encoded.outputs["Vector"], mapping.inputs["Color"])
    tree.links.new(mapping.outputs["Normal"], bsdf.inputs["Normal"])
