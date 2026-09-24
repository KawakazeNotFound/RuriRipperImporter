"""The view a vertex tree is evaluated for, kept as one object the trees read.

A geometry tree is evaluated once per dependency graph. It has a node for the scene's active camera and none for the
3D viewport it is drawn in -- yet an outline a source draws is defined against whoever is looking: its width is solved
in screen pixels and it pushes each vertex along the screen projection of the normal. Read from the scene camera, that
outline is drawn for a camera the user is not looking through, and a scene without a camera has no outline at all.

The viewpoint stands in the viewer's place: a single-point mesh linked into no scene, so nothing draws, selects or
renders it, while every tree that names it still evaluates it. Its object transform is the view's camera-to-world
transform; its point carries the view's projection matrix, its clip range with the orthographic flag, the pixel size
of what is being drawn, and the render output's pixel size. A final render is evaluated for the scene camera rather
than for any viewport -- the trees tell the two apart with Is Viewport -- so the render output's size rides along for
them to switch to. With an interface the viewpoint follows the 3D viewport the user last moved; without one it follows
the scene camera, so a background run evaluates what a render would see.

Every write re-evaluates each tree that reads the viewpoint, so a write happens only when what it carries changed, and
a file without a viewpoint costs the poll nothing: the object is found once per file load or undo step, never by
scanning on a tick.
"""

from __future__ import annotations

import traceback

import bpy
import mathutils

#: Marker the viewpoint is found by; its name is the user's to change.
MARKER = "ruri_viewpoint"
NAME = "Ruri Viewpoint"
PROJECTION = "ruri_view_projection"
FRAME = "ruri_view_frame"
SCREEN = "ruri_view_screen"
RENDER_SCREEN = "ruri_render_screen"
LAYOUT = ((PROJECTION, "FLOAT4X4"), (FRAME, "FLOAT_VECTOR"), (SCREEN, "FLOAT_VECTOR"), (RENDER_SCREEN, "FLOAT_VECTOR"))
#: How often the interface is asked whether a 3D viewport moved.
POLL_SECONDS = 1.0 / 30.0

_objects = []
_views = {}
_driver = [None]
_written = [None]


class Viewpoint:
    """The viewpoint object and the names of the point attributes it carries."""

    __slots__ = ("object", "projection", "frame", "screen", "render_screen")

    def __init__(self, obj):
        self.object = obj
        self.projection = PROJECTION
        self.frame = FRAME
        self.screen = SCREEN
        self.render_screen = RENDER_SCREEN


def viewpoint():
    """The viewpoint, made on first use and brought up to date before it is handed out."""
    if not _objects or not _alive():
        _rescan()
    if not _objects:
        _objects.append(_make())
    sync()
    return Viewpoint(_objects[0])


def sync(scene=None):
    """Bring every viewpoint to the view it stands for: the 3D viewport the user last moved, else the scene camera.
    Returns whether anything was written."""
    if _objects and not _alive():
        _rescan()
    if not _objects:
        return False
    scene = scene if scene is not None else bpy.context.scene
    if scene is None:
        return False
    state = _viewport_state()
    if state is None:
        state = _camera_state(scene)
    signature = (state, _render_screen(scene))
    if signature == _written[0]:
        return False
    for obj in _objects:
        _write(obj, state, signature[1])
    _written[0] = signature
    return True


def sync_footprint(scene):
    """Keep the world size of one render output pixel on the scene, under every name a loaded stack reads it by:
    (orthographic term, perspective term per unit of view depth), from the render camera's projection at the output
    size -- two over the vertical scale over the output height, the perspective term for a perspective camera and
    the orthographic one otherwise. A final render is what a pipeline's screen-space pass is sized against; a
    viewport has no shader-side switch to the viewport's own size. Returns how many values were written."""
    from . import material_builder

    names = material_builder.render_footprint_attributes()
    state = _camera_state(scene) if names else None
    if state is None:
        return 0
    projection = _matrix(state[1])
    size = 2.0 / (projection[1][1] * state[3][1])
    footprint = (0.0, size, 0.0) if projection[3][3] < 0.5 else (size, 0.0, 0.0)
    written = 0
    for name in names:
        if tuple(scene.get(name, ())) != footprint:
            scene[name] = footprint
            written += 1
    return written


def _alive():
    try:
        return all(obj.get(MARKER) for obj in _objects)
    except ReferenceError:
        return False


def _rescan():
    _objects[:] = [obj for obj in bpy.data.objects if obj.get(MARKER)]
    _written[0] = None


def _make():
    mesh = bpy.data.meshes.new(NAME)
    mesh.vertices.add(1)
    obj = bpy.data.objects.new(NAME, mesh)
    obj[MARKER] = 1
    _layout(mesh)
    _written[0] = None
    return obj


def _layout(mesh):
    for name, kind in LAYOUT:
        attribute = mesh.attributes.get(name)
        if attribute is not None and (attribute.data_type != kind or attribute.domain != "POINT"):
            mesh.attributes.remove(attribute)
            attribute = None
        if attribute is None:
            mesh.attributes.new(name, kind, "POINT")


def _write(obj, state, render):
    mesh = obj.data
    _layout(mesh)
    attributes = mesh.attributes
    if state is None:
        attributes[FRAME].data[0].vector = (0.0, 0.0, 0.0)
    else:
        transform, projection, frame, screen = state
        obj.matrix_world = _matrix(transform)
        attributes[PROJECTION].data[0].value = _matrix(projection)
        attributes[FRAME].data[0].vector = frame
        attributes[SCREEN].data[0].vector = (screen[0], screen[1], 0.0)
    attributes[RENDER_SCREEN].data[0].vector = (render[0], render[1], 0.0)
    mesh.update()


def _flat(matrix):
    return tuple(float(value) for row in matrix for value in row)


def _matrix(flat):
    return mathutils.Matrix((flat[0:4], flat[4:8], flat[8:12], flat[12:16]))


def _clip_range(projection):
    """Near and far clip planes of a GL projection matrix, perspective or orthographic."""
    a = projection[2][2]
    b = projection[2][3]
    if projection[3][3] > 0.5:
        return (b + 1.0) / a, (b - 1.0) / a
    return b / (a - 1.0), b / (a + 1.0)


def _frame(projection):
    near, far = _clip_range(projection)
    return near, far, 1.0 if projection[3][3] > 0.5 else 0.0


def _render_screen(scene):
    render = scene.render
    scale = render.resolution_percentage / 100.0
    return float(render.resolution_x) * scale, float(render.resolution_y) * scale


def _viewport_state():
    """The state of the 3D viewport the user last moved: a viewport whose view changed since the last look takes
    over, and with none moving the one already followed stays, or the largest one when it is gone. A background run
    has none -- its window manager still holds the startup file's screens, but nothing is ever drawn through them."""
    manager = bpy.context.window_manager
    if bpy.app.background or manager is None:
        return None
    views = {}
    for window in manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((one for one in area.regions if one.type == "WINDOW"), None)
            view = getattr(area.spaces.active, "region_3d", None)
            if region is None or view is None or region.width <= 1 or region.height <= 1:
                continue
            window_matrix = view.window_matrix
            views[area.as_pointer()] = (_flat(view.view_matrix.inverted()), _flat(window_matrix),
                                        _frame(window_matrix), (float(region.width), float(region.height)))
    if not views:
        _views.clear()
        _driver[0] = None
        return None
    moved = [key for key, state in views.items() if key in _views and _views[key] != state]
    if moved and _driver[0] not in moved:
        _driver[0] = moved[0]
    elif _driver[0] not in views:
        _driver[0] = max(views, key=lambda key: views[key][3][0] * views[key][3][1])
    _views.clear()
    _views.update(views)
    return views[_driver[0]]


def _camera_state(scene):
    camera = scene.camera
    if camera is None:
        return None
    depsgraph = bpy.context.evaluated_depsgraph_get()
    width, height = _render_screen(scene)
    render = scene.render
    projection = camera.calc_matrix_camera(depsgraph, x=int(round(width)), y=int(round(height)),
                                           scale_x=render.pixel_aspect_x, scale_y=render.pixel_aspect_y)
    return (_flat(camera.evaluated_get(depsgraph).matrix_world), _flat(projection), _frame(projection),
            (width, height))


def _poll():
    try:
        sync()
    except Exception:
        traceback.print_exc()
    return POLL_SECONDS


@bpy.app.handlers.persistent
def _on_data_replaced(*_args):
    # Opening a file or stepping undo replaces the data the cached objects and the written state describe.
    _rescan()


def register():
    handlers = bpy.app.handlers
    for chain in (handlers.load_post, handlers.undo_post, handlers.redo_post):
        if _on_data_replaced not in chain:
            chain.append(_on_data_replaced)
    if not bpy.app.background and not bpy.app.timers.is_registered(_poll):
        bpy.app.timers.register(_poll, first_interval=POLL_SECONDS, persistent=True)


def unregister():
    if bpy.app.timers.is_registered(_poll):
        bpy.app.timers.unregister(_poll)
    handlers = bpy.app.handlers
    for chain in (handlers.load_post, handlers.undo_post, handlers.redo_post):
        if _on_data_replaced in chain:
            chain.remove(_on_data_replaced)
    _objects.clear()
    _views.clear()
    _driver[0] = None
    _written[0] = None
