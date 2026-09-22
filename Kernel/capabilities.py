"""What a host can do, as protocols it implements -- declared once, by being one.

The kernel talks to exactly one object that is application-shaped: the bound
driver. What that driver can do used to be said TWICE -- a set of capability
strings beside a class with a method per capability, every method abstract, so a
host with no rigs still had to carry a ``rig_rest`` that raises. Two statements
of one fact drift, and the drift is silent: a host that gained a method and
forgot the string offered nothing, and one that gained the string and forgot the
method crashed three stages into an import.

So there is one statement. A driver derives from :class:`Toolkit` -- every host
is one -- and from whichever of the other protocols it can actually answer.
:func:`capabilities` reads that back with ``isinstance``. There is no stub to
write and nothing to keep in step: a host that cannot pose a skeleton simply is
not a :class:`Rig`, every option, command, tab and section that names ``Rig`` is
ABSENT there rather than disabled, and a new host answers by deriving.

No protocol is named after a host, and no protocol's methods name one.
"""

from __future__ import annotations

import abc

#: The bound driver IS process state -- reloading this module during development
#: would unbind it while the application it names is still very much running,
#: and every module reloaded after this one would then fail asking for its host.
HOLDS_PROCESS_STATE = True

DEBUG = "debug"
INFO = "info"
WARNING = "warning"
ERROR = "error"


class Toolkit(abc.ABC):
    """The application itself: where it puts things, how it says things, how it
    is asked to do the one thing every host does -- materialise a statement."""

    #: Folder name of this driver under ``Host/`` -- also the name of the
    #: per-host subfolder a generated shader stack is projected into (see
    #: :mod:`Kernel.shaderstack`). One string, two uses, no mapping table.
    name = ""

    @abc.abstractmethod
    def log(self, level, message):
        """Write one line where this application's users look for messages."""

    @abc.abstractmethod
    def workspace_dir(self):
        """Root for everything this toolchain generates, or None to let
        :mod:`Kernel.bridge.workspace` pick the per-user data folder. Never
        inside the checkout: a checkout is replaced wholesale by a pull."""

    @abc.abstractmethod
    def preset_dir(self):
        """Where THIS application keeps the preset files its users author, or
        None when it has no such place and the workspace is the only home."""

    @abc.abstractmethod
    def bin_dir(self):
        """The built folder that directly contains ``Ruri.RipperHook.dll``. The
        one genuinely machine-specific path."""

    @abc.abstractmethod
    def bin_dir_hint(self):
        """One sentence telling THIS application's user where to set it."""

    @abc.abstractmethod
    def texture_containers(self):
        """Image containers this application loads directly, as lowercase
        extensions, or () to take every texture in whatever container the game
        itself shipped."""

    @abc.abstractmethod
    def locale(self):
        """The language code this application's UI is running in, e.g.
        ``zh_CN`` -- what a game's own localized names are joined through."""

    @abc.abstractmethod
    def absolute_path(self, path):
        """Resolve a path the user typed, in this application's own idiom."""

    @abc.abstractmethod
    def schedule(self, seconds, call):
        """Run ``call`` once, ``seconds`` from now, on the main thread. ``call``
        returns a delay to run again, or None to stop."""

    @abc.abstractmethod
    def redraw(self):
        """Ask the application to repaint the plugin's surfaces."""

    @abc.abstractmethod
    def register_state(self, name, schema, handlers, extra=None):
        """Materialise a panel's state declaration and file it under ``name``."""

    @abc.abstractmethod
    def unregister_state(self, name):
        """Drop what :meth:`register_state` filed under ``name``."""

    @abc.abstractmethod
    def panel_state(self, context, name):
        """The record filed under ``name``."""

    @abc.abstractmethod
    def materialise(self, context, statement, options, report=None):
        """Put what the kernel stated into this document.

        ``statement`` is :class:`Kernel.statement.Statement` -- the nodes,
        meshes, skeletons, materials, textures, morphs and clips of a selection,
        already in this host's own basis. The ONE place the two hosts' import
        pipelines are named, and deliberately the only one: a panel resolves a
        selection to seeds, asks the kernel what they are, and hands the answer
        over. Blender builds a rig, objects and node materials; Painter writes
        one self-contained mesh file and wires its texture sets. Neither is a
        lesser version of the other, and neither is a branch in the panel that
        asked. Returns :class:`Kernel.statement.Built`."""


class SceneGraph(abc.ABC):
    """A host that materialises a scene as a HIERARCHY of separate objects, each
    with its own transform. A project that IS one mesh file is not the same
    thing under a different name -- it is a merge."""

    @abc.abstractmethod
    def clear_scene(self, context):
        """Empty the document before an import puts something new in it."""


class Rig(abc.ABC):
    """A host that materialises a skeleton as a first-class object the user can
    pose, and that can remember things on it."""

    @abc.abstractmethod
    def selected_rig(self, context):
        """The skeleton the user has in front of them right now, or None."""

    @abc.abstractmethod
    def rig_named(self, rig_name, context=None):
        """The rig this document knows by that name, or None."""

    @abc.abstractmethod
    def rig_memory(self, rig):
        """A mutable mapping of what the plugin remembers ON one rig. It is the
        rig itself that must remember: a later session opens the document and
        the panel state is gone, while the character is still there."""

    @abc.abstractmethod
    def rig_rest(self, context, rig):
        """``[{"name", "rest"}]`` -- every bone of this rig that carries a
        source-space rest local, under the SOURCE's own bone names."""

    @abc.abstractmethod
    def rig_seed(self, rig):
        """The seed this rig was built FROM, or "" -- what a later question about
        this character is asked with. Carried verbatim from the kernel to the
        kernel; this side never reads into it, because how a seed is spelled is
        the claiming reader's own answer."""

    @abc.abstractmethod
    def rig_avatar(self, rig):
        """The avatar stamped on this rig when it was built, or "" -- what a
        muscle-encoded performance has to be solved against. Carried verbatim
        from the kernel to the kernel; this side never reads into it."""

    @abc.abstractmethod
    def write_secondary_motion(self, context, rig, reading):
        """Write a model's own hair/cloth/accessory chains onto ``rig``, as the
        kernel stated them. Returns the lines to word."""


class Timeline(abc.ABC):
    """A host with an animation surface: channels, a playhead, a frame rate."""

    @abc.abstractmethod
    def frame_rate(self, context):
        """Frames per second of the document's own timeline."""

    @abc.abstractmethod
    def set_frame_range(self, context, start, end):
        """Aim the playhead at what was just built."""

    @abc.abstractmethod
    def play_clips(self, context, rig, clips, options, activate=False):
        """Build the stated clips onto ``rig`` as this host's own animation
        channels. ``clips`` are :class:`Kernel.statement.StatementClip` rows --
        a JSON index beside a float32 curve payload, already re-anchored to that
        rig's bone paths. Returns (built, lines)."""

    @abc.abstractmethod
    def bake_bone_poses(self, context, rig, source_names, frame_count, payload,
                        name, into=None):
        """Key a block of per-frame source-space locals onto this rig's bones.
        ``payload`` is float32, ``frame_count`` x ``len(source_names)`` x 10
        (position, quaternion, scale). Returns how many bones were posed."""


class Director(abc.ABC):
    """A host that can put a scripted MOMENT into the document.

    A staged moment is not one object and not one performance: it is a set, a
    cast standing on it, shots cutting between virtual cameras, motion on each
    performer and lines said at stated seconds. A host answers this when it has
    somewhere to put all of that at once -- a hierarchy, a playhead and a camera
    -- and a host that has none of those simply does not offer the tab.

    The DIRECTIVE STREAM is the whole contract: rows saying what to do, in
    seconds, against names, with the seed of whatever each row needs loaded. A
    directive kind this host has not implemented is a row it marks on the
    timeline rather than one that stops the build, which is what lets a build
    state more than a host plays without either side breaking.
    """

    @abc.abstractmethod
    def build_stage(self, context, label, directives, options):
        """Realize one stage. ``directives`` are the stream's rows as plain
        dicts, in time order. Returns (built, lines)."""

    @abc.abstractmethod
    def advance_stage(self, context, step):
        """Move the playhead one beat forward (step 1) or back (-1), and return
        what is now current as a line to show, or "" when there is no script."""


class MorphTargets(abc.ABC):
    """A host with morph targets, which a facial expression library drives."""

    @abc.abstractmethod
    def face_bindings(self, context, rig, table):
        """What a ctrl-driven face TABLE actually reaches on this rig. Returns
        ``{"ctrls", "via", "missing_bones", "rest_error", "reason"}``."""

    @abc.abstractmethod
    def drive_face(self, context, rig, table, weights):
        """Drive every bound ctrl to its weight and every other one to zero, so
        a pose REPLACES the face rather than piling onto the last one."""

    @abc.abstractmethod
    def bake_face(self, context, rig, table, tracks, frames, fps, name, into=None):
        """Bake one ctrl-driven animation as this host's own channels."""

    @abc.abstractmethod
    def drive_blend_shapes(self, context, rig, weights):
        """Set blend shapes on the meshes ``rig`` drives, as
        ``{mesh name: {index: value}}``. Returns (meshes touched, warnings)."""


class NodeMaterials(abc.ABC):
    """A host whose materials are NODE GRAPHS the plugin builds and can share as
    reusable groups -- which is what makes "rebuild the game's own shading
    stack" and "where do its templates live" questions that exist at all."""

    @abc.abstractmethod
    def shader_stacks(self):
        """The generated stacks plugged into this host, by game name."""


class TextureSets(abc.ABC):
    """A host that groups surfaces into fixed-resolution texture sets."""

    @abc.abstractmethod
    def texture_set_plan(self, statement, options):
        """How the stated materials fall into this host's texture sets."""


class Display(abc.ABC):
    """A host whose viewport display -- environment map, tone mapping, colour
    LUT, and whatever a game's own display stage states -- is settable by the
    plugin."""

    @abc.abstractmethod
    def load_display_stage(self, context, stage, options):
        """Put one of a game's own display stages into the document, as the
        kernel stated it. Returns the lines to word."""


#: Every protocol, in the order a diagnostics surface should list them. Named
#: here so a panel can word "this host cannot do that" without importing each.
PROTOCOLS = (Toolkit, SceneGraph, Rig, Timeline, Director, MorphTargets,
             NodeMaterials, TextureSets, Display)

_BOUND = []


def bind(host):
    """Install the driver for this process. Called once, by the driver itself,
    before anything else in the kernel runs."""
    if not isinstance(host, Toolkit):
        raise TypeError("a host driver must derive from Kernel.capabilities.Toolkit, got "
                        + type(host).__name__)
    if not getattr(host, "name", ""):
        raise ValueError("host driver declares no name")
    _BOUND[:] = [host]
    return host


def current():
    """The bound driver. Raises rather than returning a stand-in: a kernel that
    can run with no host is a kernel with a second, invisible host."""
    if not _BOUND:
        raise RuntimeError(
            "no host driver is bound -- Host/<name>/__init__.py binds one at import, "
            "so reaching here means the kernel was imported outside a driver.")
    return _BOUND[0]


def bound():
    """True once a driver is installed -- for the handful of places that
    legitimately run before one is (a module body computing a constant)."""
    return bool(_BOUND)


def capabilities(host=None):
    """Which protocols the bound driver answers, read off the driver itself."""
    host = current() if host is None else host
    return frozenset(protocol for protocol in PROTOCOLS if isinstance(host, protocol))


def supports(protocol, host=None):
    return isinstance(current() if host is None else host, protocol)


def log(message, level=INFO):
    current().log(level, message)
