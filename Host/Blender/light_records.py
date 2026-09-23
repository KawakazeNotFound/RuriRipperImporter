"""A source pipeline's own record of each of its lights, stamped on the light a statement made for it.

A stack whose light loop lights through the source's own light table -- the source's attenuation
window, cone, culling box, tube and soft source rather than this host's light evaluation -- reads each
light's record as LIGHT attributes: one vector property per record vector on the light object, under
the names the stack declares (see :data:`material_builder.LIGHT_RECORDS`). A statement's light carries
the source's own key for it (:data:`SOURCE_LIGHT_PROPERTY`), and that is what a record is matched to:
Blender renames an object whose name is taken, the key stays.

A table follows its viewer -- the source fades each light by camera distance and culls it past its
distances -- so one set of records is one viewer's: a light the source does not draw from there is
hidden, one it draws carries its record. Only changed values are written: an ID property re-evaluates
its light, and rewriting the same value would re-sync every light for nothing.
"""

from __future__ import annotations

from . import material_builder

#: Custom property on a light object a statement made: the source's own key for that light.
SOURCE_LIGHT_PROPERTY = "ruri_source_light"


def attribute_names():
    """The record's attribute names in record order, as every loaded stack that reads records states
    them. Stacks reading none are not counted; two stacks reading different records cannot share one
    light and are refused."""
    layouts = {tuple(provider()) for provider in material_builder.LIGHT_RECORDS}
    layouts.discard(())
    if len(layouts) > 1:
        raise RuntimeError(
            "[light-records] the loaded shading stacks read different light records {0}; they come from "
            "different generator builds -- redeploy the stale ones".format(sorted(layouts)))
    return list(next(iter(layouts))) if layouts else []


def apply(scene, records):
    """Stamp one viewer's records onto the lights of ``scene`` a statement made.

    ``records`` maps a light's source key to ``(visible, vectors)``: whether the source draws it from
    the viewer, and its record as one ``(x, y, z, w)`` per vector. Returns ``(stamped, unmatched)``: how
    many lights were written, and the names of the stated lights no record was supplied for."""
    names = attribute_names()
    if not names:
        return 0, []
    stamped = 0
    unmatched = []
    for obj in scene.objects:
        key = obj.get(SOURCE_LIGHT_PROPERTY) if obj.type == "LIGHT" else None
        if key is None:
            continue
        record = records.get(key)
        if record is None:
            unmatched.append(obj.name)
            continue
        visible, vectors = record
        if len(vectors) != len(names):
            raise ValueError("[light-records] light {0} carries {1} record vectors; the stacks read {2}".format(
                key, len(vectors), len(names)))
        hidden = not visible
        if obj.hide_render != hidden:
            obj.hide_render = hidden
        if obj.hide_viewport != hidden:
            obj.hide_viewport = hidden
        for name, vector in zip(names, vectors):
            value = [float(component) for component in vector]
            current = obj.get(name)
            if current is None or list(current) != value:
                obj[name] = value
        stamped += 1
    return stamped, unmatched
