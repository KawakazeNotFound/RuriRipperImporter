"""A level's deferred decals, handed to the objects their boxes reach.

The source projects each decal box into its GBuffer between the GBuffer pass and deferred lighting;
a host shading each surface in one pass applies the decals inside the material instead, and a
material can only afford the boxes that can reach its own object. Each object's list is the indices
-- in drawing order, the order of the level's decal records -- of the boxes whose world bounds meet
the object's world bounds: a conservative cut, since the material tests every pixel against the box
itself. Only objects with a material that reads the per-object global get a list -- which materials
read it is whatever their graphs say (an object attribute node of that name, at any group depth).
The lists of all objects go end to end into one data table; each object carries where its run starts
and how many entries it has as a per-object global (the value minus the default the stacks declare,
the encoding every per-object global uses), and an object no box reaches carries none, so it reads
the default: no decals.
"""
import numpy
from mathutils import Matrix, Vector

from . import material_builder

_UNIT_CORNERS = [Vector((x, y, z, 1.0)) for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5)]


def apply(context, boxes, range_attribute, list_table):
    """Bind ``boxes`` -- the level's decals in drawing order, each the column-major matrix taking the
    unit cube onto its box in the SOURCE's world -- to the objects they reach, through the per-object
    global ``range_attribute`` and the data table ``list_table`` the stacks read. Returns the lines to
    report."""
    base = material_builder.object_attribute_base(range_attribute)
    layout = material_builder.level_image_layout(list_table)
    if base is None or layout is None:
        return ["no shading stack reads decal lists ({0}, {1})".format(range_attribute, list_table)]
    basis = Matrix(material_builder.world_basis()).to_4x4()
    bounds = [_bounds([(basis @ (_matrix(columns) @ corner)).xyz for corner in _UNIT_CORNERS]) for columns in boxes]
    depsgraph = context.evaluated_depsgraph_get()
    readers = {}
    entries = []
    reached = 0
    for obj in context.scene.objects:
        if obj.type != "MESH":
            continue
        if not any(slot.material is not None and slot.material.node_tree is not None
                   and _reads(slot.material.node_tree, range_attribute, readers) for slot in obj.material_slots):
            if range_attribute in obj:
                del obj[range_attribute]
            continue
        evaluated = obj.evaluated_get(depsgraph)
        low, high = _bounds([evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box])
        hits = [index for index, (box_low, box_high) in enumerate(bounds)
                if all(low[axis] <= box_high[axis] and box_low[axis] <= high[axis] for axis in range(3))]
        if not hits:
            if range_attribute in obj:
                del obj[range_attribute]
            continue
        obj[range_attribute] = [float(len(entries)) - base[0], float(len(hits)) - base[1], -base[2], -base[3]]
        entries.extend(hits)
        reached += 1
    capacity = int(layout["size"][1])
    if len(entries) > capacity:
        raise ValueError("[decals] {0} list entries for {1} object(s); the stacks' {2} holds {3}".format(
            len(entries), reached, list_table, capacity))
    rows = numpy.zeros((len(entries), 1, 4), dtype=numpy.float32)
    rows[:, 0, 0] = entries
    material_builder.write_level_table(list_table, rows)
    return ["{0} decal(s) reach {1} object(s)".format(len(boxes), reached)] if boxes else []


def _reads(tree, name, readers):
    """Whether ``tree`` reads the per-object global ``name``, through any depth of groups (memoised per tree)."""
    key = tree.as_pointer()
    known = readers.get(key)
    if known is None:
        known = readers[key] = any(
            (node.bl_idname == "ShaderNodeAttribute" and node.attribute_type == "OBJECT" and node.attribute_name == name)
            or (node.bl_idname == "ShaderNodeGroup" and node.node_tree is not None and _reads(node.node_tree, name, readers))
            for node in tree.nodes)
    return known


def _matrix(columns):
    """A column-major 4x4 as a matrix."""
    return Matrix([columns[0:4], columns[4:8], columns[8:12], columns[12:16]]).transposed()


def _bounds(points):
    return (Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
            Vector(tuple(max(point[axis] for point in points) for axis in range(3))))
