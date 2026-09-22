"""Cross-game animation retarget: play any game's animation on any rig.

  clip 绑定 CRC ─(m_TOS 覆盖率)─> 源 Avatar ─(cabmap 反向依赖 + 根 Animator 身份)─> 宿主角色 prefab

One decision, and it is a MEASUREMENT: a clip whose bindings land on the target rig
binds directly, and only one that does not goes through the declared table graph.
The rig's bones carry the Unity transform each of them is (``rig_identity``), so
"is this that clip's skeleton" is counted rather than inferred from what the rig is
called or which family it declares -- see load_clips_onto for why the inferred
answer was the wrong one.

One builder: the host is imported through the ordinary prefab path, the same one a
user's own character import runs. One maths: the named preset goes verbatim
(mappings AND settings) to AnimationRetarget, which skips missing bones itself.
One file per pair: that preset also carries the ``face`` section this pair's
expressions cross on (``face_ir``), so a body and its head are never chosen out of
two places that can disagree. Nothing here reads a name, a folder or a game; what a
face IS stays game-specific (``Game.face_retarget_of``).
"""

from __future__ import annotations

import collections

import bpy

from . import armature_builder, prefab_importer
from ...Kernel import face_ir
from ... import Game
from ...Kernel.bridge import cabmap_state
from ...Kernel.unity import class_registry, clip_paths


ADDON_MODULE = "AnimationRetarget"

# How much of a clip's own bindings must land on a rig for it to BE that clip's
# skeleton. A renamed, grafted or merged rig still binds every path it kept, so a
# real match is total or near it; a genuinely different skeleton shares a handful
# of standard names at most. Anything in between is the interesting case, and it
# takes the table -- which is the branch that can say what it could not carry.
DIRECT_BINDING_RATIO = 0.95


def _addon():
    """The AnimationRetarget add-on's (core, presets, api) modules, or None when it is
    not installed -- imported lazily by name so this importer still loads without it."""
    try:
        core = __import__(ADDON_MODULE + ".core", fromlist=["core"])
        presets = __import__(ADDON_MODULE + ".presets", fromlist=["presets"])
        api = __import__(ADDON_MODULE + ".api", fromlist=["api"])
    except ImportError:
        return None
    return core, presets, api


def _compose():
    """AnimationRetarget's preset-composition engine, or None.

    THE one implementation of "which tables join these two skeleton families, and
    what does the joined table look like". It lives over there because that is
    where the presets live -- a second copy here would be a second answer to the
    same question, and the two would drift the first time either grew a rule."""
    try:
        return __import__(ADDON_MODULE + ".compose", fromlist=["compose"])
    except ImportError:
        return None


def available():
    return _addon() is not None


SKELETON_PROP = "ruri_skeleton"


def skeleton_of(arm_obj):
    """The skeleton family this rig belongs to: its own declaration, else the game it
    was imported from. One studio ships one family across many titles, so families are
    declared -- in-file on presets, on the rig here -- and filenames mean nothing."""
    if arm_obj is None:
        return ""
    return str(arm_obj.get(SKELETON_PROP) or "") or armature_builder.read_game(arm_obj)


def set_skeleton(arm_obj, name):
    if arm_obj is not None:
        arm_obj[SKELETON_PROP] = str(name or "")


def bone_names(arm_obj):
    """This rig's own bone names -- the observation that says WHICH of a skeleton
    family's configs (Girl / Boy) it is, when the name it carries only says the
    family."""
    if arm_obj is None or arm_obj.type != "ARMATURE" or arm_obj.data is None:
        return ()
    return tuple(bone.name for bone in arm_obj.data.bones)


def resolve_retarget_spec(session_key, dest_arm):
    """(composed spec, label) joining the session's skeleton to this rig's.

    Every preset declares which two skeletons it bridges (``source`` / ``dest``, each
    a ``{family, config}`` plus that family's ``aliases`` -- so a studio that changes
    its shop sign, and sister titles sharing one rig, all share the one table). Neither
    end of a real call names a config, though: a session knows a GAME (the alias) and a
    rig carries a FAMILY (``ruri_skeleton``, stamped game as default). So the config is
    settled by ``route_for`` from this rig's actual bones plus which pairs the tables
    can reach at all -- never from the name. Same skeleton, or a name nothing declares
    = ({}, ""), the direct-bind path.

    The graph walk and the join are AnimationRetarget's (see ``compose``), because
    they are about ITS presets -- this only supplies the two ends and words the
    answer. A pair with no direct table composes through whatever chain the graph
    offers, so KoikatuToEndfield + EndfieldToWaifu already IS Koikatu -> Waifu.
    """
    compose = _compose()
    if compose is None:
        return {}, ""
    source_id = str(cabmap_state.game_of(session_key) or "")
    dest_id = skeleton_of(dest_arm)
    if not source_id or not dest_id:
        return {}, ""
    edges = compose.load_edges()
    route = compose.route_for(source_id, dest_id, edges,
                              dest_bones=bone_names(dest_arm))
    if route is None or not route.hops:
        return {}, ""
    return compose.compose(route, edges), route.via


def _no_table_message(session_key, dest_arm):
    """Why nothing joined these two skeletons, worded as the thing to go fix -- or ""
    when there was nothing to join in the first place.

    Four different repairs hide behind the one dead end -- a game name nobody listed as
    an alias, a pair nobody wrote a table for, a family whose configs this rig's bones
    do not tell apart, and a chain that exists but joins to nothing -- and sending the
    user to the wrong one of the four costs a whole editing session. So each is named.

    Whether the two names are the same skeleton at all is ``route_for``'s answer, not a
    string comparison here: an alias makes two different names one skeleton (a session
    browsing 'Waifu' onto a rig stamped 'Ruri'), and comparing the text would report a
    missing table for a pair that never needed one."""
    source_id = str(cabmap_state.game_of(session_key) or "")
    dest_id = skeleton_of(dest_arm)
    if not source_id or not dest_id:
        return ""
    compose = _compose()
    if compose is None:
        return ("The AnimationRetarget add-on is not enabled, so '{0}' and '{1}' cannot be "
                "joined by any bone table.".format(source_id, dest_id))
    edges = compose.load_edges()
    dest_bones = bone_names(dest_arm)
    route = compose.route_for(source_id, dest_id, edges, dest_bones=dest_bones)
    if route is not None:
        if not route.hops or compose.compose(route, edges).get("mappings"):
            return ""
        return ("{0} composes to no shared bone at all -- the chain exists but an "
                "intermediate skeleton drops every row. Write a direct table for this "
                "pair, or widen the one in the middle.".format(route.label()))
    starts = compose.sides_for(source_id, edges)
    finishes = compose.narrowed(compose.sides_for(dest_id, edges), dest_bones, edges)
    unknown = [name for name, found in ((source_id, starts), (dest_id, finishes)) if not found]
    if unknown:
        return ("No preset declares the skeleton {0} -- add the name to that family's "
                "\"aliases\" in a preset's source/dest, or write the table it belongs to."
                .format(" or ".join(repr(name) for name in unknown)))
    routed = compose.routes_between(starts, finishes, edges)
    if len(routed) > 1:
        return ("'{0}' reaches '{1}' more than one way ({2}), and '{3}' bones do not tell "
                "those skeletons apart -- set its {4} to one of {5}.".format(
                    source_id, dest_id, ", ".join(option.label() for option in routed),
                    dest_arm.name, SKELETON_PROP,
                    ", ".join(repr(side.key) for side in finishes)))
    return ("No table chain joins skeleton '{0}' to '{1}' -- write the pair as a preset's "
            "source/dest ({2} -> {3}); chains compose automatically, so one table to any "
            "skeleton already reachable from the other end is enough.".format(
                source_id, dest_id,
                "/".join(side.key for side in starts),
                "/".join(side.key for side in finishes)))


class CrossGameRetargetError(RuntimeError):
    """A direct cross-game clip import that cannot proceed: no source avatar covers the
    clips' bindings, or no bone table exists (the message then carries the fill-it-in
    prompt), or the AnimationRetarget add-on is missing."""


_AvatarScore = collections.namedtuple(
    "_AvatarScore", "cab name dependency_count score coverage tos_size")

_SOURCE_AVATAR_CACHE = {}


def _carries(rows, index, *class_names):
    """Whether one cabmap row carries every one of these classes.

    Read off the row table's own statement of what the row holds -- the decoder
    writes it as the engine's class names (CabRows.TypeNames), so this side neither
    re-derives it from the map nor keeps a second encoding of it. Matched whole
    rather than as text: 'Avatar' is not 'AvatarMask'."""
    carried = {name.strip() for name in str(rows.cell(index, "type_names") or "").split(",")}
    return all(name in carried for name in class_names)


def _candidate_avatar_cabs(session_key):
    """Every CAB in the source install's loaded cabmap that carries an Avatar, cheapest
    (fewest cabmap dependencies) first -- the search order for the source rig."""
    session = cabmap_state.session_for(session_key)
    rows = session.ROWS
    avatar_id = class_registry.id_for_name("Avatar")
    if avatar_id is None:
        raise CrossGameRetargetError("The class registry has no 'Avatar' class id.")
    candidates = []
    for index in range(len(rows)):
        if _carries(rows, index, "Avatar"):
            candidates.append((int(rows.cell(index, "deps")), rows.cell(index, "cab")))
    candidates.sort(key=lambda pair: pair[0])
    return candidates, avatar_id


def _avatar_documents(unity_file):
    for document in unity_file.documents:
        if document.class_name == "Avatar":
            yield document


_ScannedAvatar = collections.namedtuple(
    "_ScannedAvatar", "cab name dependency_count tos_size crcs")

_AVATAR_INDEX = {}


def _avatar_index(session_key):
    state = _AVATAR_INDEX.get(session_key)
    if state is None:
        candidates, _avatar_id = _candidate_avatar_cabs(session_key)
        state = {"order": candidates, "position": 0, "seen": [], "parsed": set()}
        _AVATAR_INDEX[session_key] = state
    return state


def _graph_avatar_cabs(session_key, clip_cab):
    """Avatar CABs the cabmap can actually REACH from this clip, cheapest first.

    Two reverse hops then forward: the clip's dependents (an AnimatorController, a
    timeline .playable, a montage/cpuanim .asset), then THEIR dependents (the prefab
    whose Animator names the controller), then those CABs' forward closures -- which is
    where an Avatar finally sits. Measured over 301 sampled clip CABs: one hop reaches an
    avatar for 2.7%, adding the second hop takes it to **33.6%**, candidate sets stay
    small (max 30) and the whole walk costs 1.8ms.

    It is not universal -- 46% of this game's AnimatorControllers have no dependent at
    all and 63% of character postmodels reference no controller (the controller is picked
    at runtime from gameplay config by entity id), which is exactly the case pelica's
    clips fall in: hop1 = 2 controllers, hop2 = 0. So this is a CANDIDATE SOURCE, not a
    judgement: whatever it returns still has to pass the same 100%-coverage test as every
    other candidate, and when it returns nothing the ordered walk runs as before. That is
    also why a wrong-but-reachable avatar (a weapon's, another actor's -- both common in
    the sample) costs nothing: it cannot cover a body clip's bindings, so it is rejected
    on measurement rather than on where it came from."""
    bridge = cabmap_state.BRIDGE
    if bridge is None or not clip_cab:
        return []
    session = cabmap_state.session_for(session_key)
    rows = session.ROWS
    index_of = cabmap_state.cab_index(session)
    hop1 = bridge.find_direct_dependents([clip_cab])
    if not hop1:
        return []
    hop2 = [cab for cab in bridge.find_direct_dependents(hop1) if cab not in set(hop1)]
    found = []
    for cab in bridge.resolve_closure_cab_names(hop1 + hop2):
        index = index_of.get(cab)
        if index is not None and _carries(rows, index, "Avatar"):
            found.append((int(rows.cell(index, "deps")), cab))
    found.sort()
    return found


def _score_of(entry, clip_crcs, want):
    hits = len(entry.crcs & clip_crcs)
    return _AvatarScore(entry.cab, entry.name, entry.dependency_count, hits,
                        hits / want if want else 0.0, entry.tos_size)


def score_source_avatars(session_key, clip_crcs, stop_at_full=True, clip_cab=None):
    """Which skeleton a clip was authored on, best first, as the reader ranks it.

    Every candidate avatar's transform table is measured against the clip's own
    binding hashes on the reader side, where the tables already are -- so this
    states the question and reads the answer."""
    from ...Kernel.bridge import cabmap_state

    if cabmap_state.BRIDGE is None or not clip_cab:
        return []
    table = cabmap_state.BRIDGE.game_data("core.clip.source_skeleton", clip=str(clip_cab))
    ranked = []
    for index in range(len(table)):
        ranked.append(_AvatarScore(str(table.cell(index, "cab")),
                                   str(table.cell(index, "skeleton")),
                                   0,
                                   int(float(table.cell(index, "hits") or 0)),
                                   float(table.cell(index, "ratio") or 0.0),
                                   int(float(table.cell(index, "tos") or 0))))
    return ranked


def _rank_key(item):
    """Best coverage first; among ties the fewest-dependency, most-complete skeleton
    (a base body rig over a garment variant that merely embeds it), then name."""
    return (-item.score, item.dependency_count, -item.tos_size, item.name)


def _resolve_source_avatar(session_key, clip_cab, clip_crcs):
    """The Avatar UnityFile the clips were authored on, plus its _AvatarScore. Cached per
    (install, clip CAB) so a second clip from the same pack skips the whole scan."""
    bridge = cabmap_state.BRIDGE
    if bridge is None:
        raise CrossGameRetargetError("No cabmap bridge session for the source game.")
    key = (session_key, clip_cab)
    cached = _SOURCE_AVATAR_CACHE.get(key)
    if cached is not None:
        unity_file = _load_source_avatar_file(bridge, session_key, cached.cab, cached.name)
        if unity_file is not None:
            return unity_file, cached
    ranked = score_source_avatars(session_key, clip_crcs, clip_cab=clip_cab)
    if not ranked or ranked[0].score == 0:
        raise CrossGameRetargetError(
            "No {0} avatar's skeleton covers the selected clip's bindings -- there is nothing "
            "to retarget from.".format(session_key))
    best = ranked[0]
    _SOURCE_AVATAR_CACHE[key] = best
    unity_file = _load_source_avatar_file(bridge, session_key, best.cab, best.name)
    if unity_file is None:
        raise CrossGameRetargetError("The chosen source avatar CAB could not be re-read.")
    return unity_file, best


def _has_action(arm_obj):
    return (arm_obj.animation_data is not None
            and arm_obj.animation_data.action is not None)


def _discard_baked(baked_actions):
    """Remove the intermediate actions baked onto the host."""
    for action in baked_actions:
        try:
            bpy.data.actions.remove(action)
        except Exception:
            pass


def _discard_host(host_objects):
    """The host lives only for the duration of one retarget call -- it is rebuilt from
    the game data whenever needed, so nothing of it ever stays in the scene."""
    blocks = []
    for obj in host_objects:
        if obj.data is not None:
            blocks.append(obj.data)
        try:
            bpy.data.objects.remove(obj, do_unlink=True)
        except Exception:
            pass
    for data in blocks:
        if data.users:
            continue
        for pool in (bpy.data.armatures, bpy.data.meshes, bpy.data.curves):
            try:
                pool.remove(data)
                break
            except Exception:
                continue


def _host_candidate_cabs(session_key, avatar_cab):
    """The CABs that could be "this character's own model prefab", cheapest first.

    Reverse dependency is CAB-granular, and a character's fbx CAB carries its Mesh
    alongside its Avatar -- so what comes back is everything that USES this character
    (measured: 183 CABs for one Endfield character -- cutscenes, dialogs, levelseqs,
    a UI model), not the host itself. **The order here only affects speed, never
    correctness**: which one is the host is answered by the hard test in
    _resolve_host_cab, and this merely puts the smallest closures first so the common
    case hits in one or two tries (measured: 2nd candidate for one character, 3rd for
    another). Carrying both a GameObject and an Animator is necessary, so that filter
    runs first and is free."""
    bridge = cabmap_state.BRIDGE
    session = cabmap_state.session_for(session_key)
    rows = session.ROWS
    index_of = cabmap_state.cab_index(session)
    ranked = []
    for cab in bridge.find_direct_dependents([avatar_cab]):
        index = index_of.get(cab)
        if index is None or not _carries(rows, index, "GameObject", "Animator"):
            continue
        closure = bridge.resolve_closure_cab_names([cab])
        ranked.append((len(closure), int(rows.cell(index, "deps")), cab))
    ranked.sort()
    ordered = [cab for _closure_size, _dependency_count, cab in ranked]
    self_index = index_of.get(avatar_cab)
    if (self_index is not None and avatar_cab not in ordered
            and _carries(rows, self_index, "GameObject", "Animator")):
        ordered.append(avatar_cab)
    return ordered


def _resolve_host_cab(session_key, source):
    """The archive and asset of the character the clips were authored on.

    One test, and it is hard: the Animator on the prefab's ROOT GameObject names
    exactly this Avatar. That test is the reader's -- it walks the candidates
    where they already are and states the winner beside the avatar it belongs
    to, so this reads the answer rather than scanning for it."""
    bridge = cabmap_state.BRIDGE
    if bridge is None:
        raise CrossGameRetargetError("No cabmap bridge session for the source game.")
    bridge.use_session(session_key)
    table = bridge.game_data("core.clip.source_skeleton", clip=str(source.cab))
    for index in range(len(table)):
        if str(table.cell(index, "skeleton")) != source.name:
            continue
        host_cab = str(table.cell(index, "host_cab"))
        host_seed = str(table.cell(index, "host_seed"))
        if host_cab or host_seed:
            return host_cab or source.cab, host_seed
    raise CrossGameRetargetError(
        "No prefab is rooted on avatar '{0}' -- the character these clips were "
        "authored on is not in this install's cabmap, so there is no rig to "
        "retarget from.".format(source.name))


def _build_host_rig(context, session_key, host, options):
    """Place the character the clips were authored on -- the ONE skeleton builder,
    the same statement path every other import takes.

    Materials, textures and performances are visual-only for a rest pose and stay
    off; everything skeletal rides the caller's own options untouched."""
    from . import packages as materialiser
    from ...Kernel.app import loading

    host_cab, host_path = host
    cabmap_state.BRIDGE.use_session(session_key)
    host_options = dict(options or {})
    host_options["import_animations"] = False
    host_options["import_materials"] = False
    host_options["import_textures"] = False
    seeds = [host_path] if host_path else [host_cab]
    known = set(bpy.data.objects)
    report = materialiser.materialise(
        context, loading.Packages(host_cab, "", loading.PREFAB, [host_cab],
                                  paths={"host": host_path} if host_path else {}),
        None, host_options)
    host_objects = [obj for obj in bpy.data.objects if obj not in known]
    for obj in host_objects:
        obj.hide_viewport = True
        obj.hide_render = True
    if report.armature is None:
        _discard_host(host_objects)
        raise CrossGameRetargetError(
            "The host character built no skeleton to bake the clips onto.")
    return report.armature, host_objects


def _host_rig_for(context, session_key, clip_cab, clip_crcs, options):
    """(host armature, its rig maps, every object imported with it) -- built fresh for
    this one call and discarded by the caller when the retarget is done."""
    _avatar_file, source = _resolve_source_avatar(session_key, clip_cab, clip_crcs)
    host_arm, host_objects = _build_host_rig(
        context, session_key, _resolve_host_cab(session_key, source), options)
    maps = prefab_importer.maps_from_stamped_armature(host_arm)
    if maps is None:
        _discard_host(host_objects)
        raise CrossGameRetargetError(
            "The host character '{0}' carries no Unity rig identity.".format(host_arm.name))
    return host_arm, maps, host_objects


def retarget_clips_onto(context, session_key, clip_cab, clip_guids, db, dest_arm, options,
                        spec, table_label, display_names=None, activate=False):
    """Import ``clip_guids`` (already resolved into ``db``, a source-game closure) onto
    ``dest_arm`` -- a rig that names a bone table -- by way of the clips' OWN host
    character. Resolves the avatar the clips measurably bind to, resolves and imports the
    character prefab rooted on that avatar, bakes the clips onto it, and hands the whole
    table (mappings AND settings) to AnimationRetarget. Returns (product_actions,
    warnings); raises CrossGameRetargetError when no avatar covers the clips, no host
    prefab is rooted on it, or the named table is unreadable/empty."""
    addon = _addon()
    if addon is None:
        raise CrossGameRetargetError(
            "The AnimationRetarget add-on is not enabled -- cross-game clip import needs its "
            "retarget maths.")
    core, _presets, api = addon

    clip_crcs = set()
    for guid in clip_guids:
        clip = db.clip_curves(guid)
        if clip is None:
            continue
        for channels in clip.transform_channel_lists():
            for channel in channels:
                if channel.path:
                    clip_crcs.add(clip_paths.entry_crc(channel.path))
    if not clip_crcs:
        raise CrossGameRetargetError("The selected clip(s) carry no transform bindings to retarget.")

    mappings = list(spec.get("mappings") or [])
    if not mappings:
        raise CrossGameRetargetError(
            "Bone table {0!r} for armature '{1}' could not be read or is empty."
            .format(table_label, dest_arm.name))

    host_arm, host_maps, host_objects = _host_rig_for(
        context, session_key, clip_cab, clip_crcs, options)

    warnings = []
    products = []
    before = set(bpy.data.actions)
    baked_actions = []
    try:
        _built, build_warnings, _actions = prefab_importer.build_selected_animations(
            db, host_arm, host_maps, None, clip_guids, options, display_names)
        warnings.extend(build_warnings)
        baked_actions = [action for action in bpy.data.actions if action not in before]
        if not baked_actions:
            raise CrossGameRetargetError("No source action baked from the selected clip(s).")

        settings = dict(spec.get("settings") or {})
        if settings.get("animated_only"):
            table = clip_paths.build_suffix_crc_table(host_maps["path_to_bone"])
            animated = set()
            for guid in clip_guids:
                clip = db.clip_curves(guid)
                if clip is None:
                    continue
                for channels in clip.transform_channel_lists():
                    for channel in channels:
                        if not channel.path:
                            continue
                        full = table.get(clip_paths.entry_crc(channel.path))
                        bone = host_maps["path_to_bone"].get(full) if full else None
                        if bone:
                            animated.add(bone)
            settings["animated_bones"] = sorted(animated)
        results, errors = api.retarget_actions(
            host_arm, dest_arm, mappings, settings, baked_actions)
        for action_name, message in errors:
            warnings.append("{0}: {1}".format(action_name, message))
        products = [dest_action for _source_action, dest_action, _info in results]
        if not products:
            raise CrossGameRetargetError(
                "Nothing retargeted onto '{0}' -- bone table '{1}' matched no shared bone.".format(
                    dest_arm.name, table_label))
        if activate or len(clip_guids) == 1 or not _has_action(dest_arm):
            core.assign_action(dest_arm, products[0])
    finally:
        _discard_baked(baked_actions)
        _discard_host(host_objects)
    return products, warnings


def load_clips_onto(context, session_key, clip_cab, clip_guids, db, dest_arm, maps, options,
                    display_names=None, activate=False):
    """THE animation-loading entry point. Every panel calls this and nothing else.

    A clip arrives from the reader already anchored on ``dest_arm``'s own bone
    paths -- a foreign skeleton's names mapped through its authoring avatar, a
    muscle encoding solved against the avatar this rig carries -- so the one
    decision left here is which rig, and the answer is the caller's."""
    from . import packages as materialiser

    seeds = ([clip_cab] if clip_cab else []) + [one for one in (clip_guids or ()) if one]
    built = materialiser.build_clips(context, "", seeds, None, options,
                                     display_names=display_names, activate=activate,
                                     rig=dest_arm)
    if not built:
        return 0, ["The picked row(s) state no performance for this skeleton."]
    return built, []


def build_clips_onto_from_closure(context, dest_arm, cabs, resolved=None):
    """One actor's performances onto its own armature, off the same statement the
    rest of the cast was placed from."""
    from . import packages as materialiser

    return materialiser.build_clips(context, "", list(cabs or ()), None,
                                    None, activate=False, rig=dest_arm)


def _face_gap(spec, table_label, dest_arm, options):
    """What the table branch could NOT do to the head, said out loud.

    A retargeted body with an untouched face is the one outcome that looks like a
    success and is not, so a pair whose table states no face section says so by
    name instead of letting the user work out why the head never moves."""
    if not options.get("retarget_face") or face_ir.section_of(spec) is not None:
        return []
    return ["Bone table '{0}' states no face section, so '{1}' got the body only -- add a "
            "\"face\" section to that table to carry expressions across this pair.".format(
                table_label, dest_arm.name)]


def _retarget_faces(context, session_key, clip_cab, clip_guids, db, dest_arm, options,
                    actions):
    """Restate each clip's baked facial performance on this rig, when the user asked
    for it and the clip's game states what a face IS.

    Lives on the ONE clip-loading path for the same reason the cross-game branch does:
    a body clip and its face are one import, and a second copy of this decision in a
    game's own panel is how the two stop agreeing. The host stays game-blind -- it asks
    the registry whether this game contributed a facial restatement and passes the clip
    through; a game with no facial system contributes none and nothing happens.

    ``actions`` is that clip's own {guid: (action, slot)} from the body build, and the
    face goes INTO it. Two reasons, both measured, and both invisible without it:

    * an object plays ONE action, so a face on its own action replaces the body it
      arrived with -- whichever the user assigns, the other half stops playing;
    * the body build already keyed the SOURCE character's facial bones onto this rig
      (same standard bone names, so they bind), which is the untranslated geometry this
      whole feature exists to avoid. Writing the face into the same action lets it
      REPLACE those channels instead of losing a fight with them.
    """
    if not options.get("retarget_face"):
        return []
    provider = Game.face_retarget_of(cabmap_state.game_of(session_key)
                                     or armature_builder.read_game(dest_arm))
    if provider is None:
        return []
    reports = []
    for guid in clip_guids:
        try:
            clip = source_anchored_clip(session_key, clip_cab, guid, db)
        except Exception as exc:
            reports.append("Face retarget skipped for one clip: {0}".format(exc))
            continue
        if clip is None:
            continue
        try:
            report = provider(context, dest_arm, clip, options, actions.get(guid))
        except Exception as exc:
            # Never silent: the body animation DID land, so a face that did not is a
            # partial result the user has to be told about by name.
            reports.append("Face retarget skipped for '{0}': {1}".format(clip.name, exc))
            continue
        if report:
            reports.append(report)
    return reports


def _binding_match(db, clip_guids, path_to_bone):
    """Best fraction of any clip's transform-curve paths that resolve to a bone of the
    target rig, and whether anything was checkable. A clip with no data, or one that
    fails to parse, is skipped -- the real per-clip complaint fires at build time."""
    best = 0.0
    checked = False
    for guid in clip_guids:
        try:
            clip = db.clip_curves(guid)
        except ValueError:
            continue
        if clip is None:
            continue
        ratio, total = clip_paths.clip_path_match_ratio(clip, path_to_bone)
        if total:
            checked = True
            best = max(best, ratio)
    return best, checked
