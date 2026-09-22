"""A level's own sky, as the world every material's environment queries read.

The source states its sky irradiance as nine spherical-harmonic coefficients per
channel -- the quantity its shading stack's SampleSH evaluates directly, irradiance
over pi, in the same pre-exposed space as the directional light. A Blender world is
RADIANCE that the renderer convolves by itself, so every band goes in divided by its
share of the cosine lobe (1, 2/3 and 1/4 for l = 0, 1, 2): convolving the result back
lands on the source's own polynomial, and a white diffuse surface under this world
reads what SampleSH would have answered for its normal.

The world has to be in place BEFORE a material is built. A material's specular answer
samples whatever world exists at build time, and one built against a flat default
world reflects that constant for good -- every surface loses its sheen and the scene
reads as flat colour. Materials already in the file are re-answered after the world
changes, through the same rewire any environment change goes through.

Directions cross into the source's axes through the shared coordinate space (the
reflection plus the once-only top-level turn), so the sky is oriented exactly like the
statement's own geometry and lights.
"""

from __future__ import annotations

import bpy
import numpy as np

from ...Kernel.math3d import coordinate
from . import material_builder

WIDTH = 512
HEIGHT = 256

_BAND_OF_COEFFICIENT = np.array([0, 1, 1, 1, 2, 2, 2, 2, 2])
_LOBE_SHARE = np.array([1.0, 2.0 / 3.0, 0.25])
_UNITY_TO_BLENDER = (coordinate.BLENDER.root_rotation @ coordinate.BLENDER.matrix)[:3, :3]


def _sample_sh(coefficients, x, y, z):
    """The source's SampleSH polynomial, per channel, in its own axes (Y up)."""
    c = coefficients[:, :, None]
    return (c[:, 0] - c[:, 6]
            + c[:, 1] * y + c[:, 2] * z + c[:, 3] * x
            + c[:, 4] * (x * y) + c[:, 5] * (y * z)
            + c[:, 6] * 3.0 * (z * z) + c[:, 7] * (z * x)
            + c[:, 8] * (x * x - y * y))


def radiance(coefficients):
    """(HEIGHT, WIDTH, 3) equirectangular radiance, bottom row first, in the texel
    layout Blender's environment lookup reads (u = -atan2(y, x) / 2pi + 1/2,
    v = atan2(z, |xy|) / pi + 1/2)."""
    stated = np.asarray(coefficients, dtype=np.float64).reshape(3, 9)
    unconvolved = stated / _LOBE_SHARE[_BAND_OF_COEFFICIENT][None, :]
    azimuth = (0.5 - (np.arange(WIDTH) + 0.5) / WIDTH) * 2.0 * np.pi
    latitude = ((np.arange(HEIGHT) + 0.5) / HEIGHT - 0.5) * np.pi
    azimuth, latitude = np.meshgrid(azimuth, latitude)
    blender = np.stack([np.cos(latitude) * np.cos(azimuth),
                        np.cos(latitude) * np.sin(azimuth),
                        np.sin(latitude)], axis=-1).reshape(-1, 3)
    source = blender @ _UNITY_TO_BLENDER
    values = _sample_sh(unconvolved, source[:, 0], source[:, 1], source[:, 2])
    return np.maximum(values.T, 0.0).reshape(HEIGHT, WIDTH, 3)


def _image(name, texels):
    stale = bpy.data.images.get(name)
    if stale is not None:
        bpy.data.images.remove(stale)
    image = bpy.data.images.new(name, WIDTH, HEIGHT, alpha=False, float_buffer=True)
    rgba = np.concatenate([texels, np.ones((HEIGHT, WIDTH, 1))], axis=-1)
    image.pixels.foreach_set(rgba.astype(np.float32).ravel())
    image.file_format = "OPEN_EXR"
    image.pack()
    return image


def build(context, coefficients, label):
    """Make the level's sky the scene's world and re-answer every built material's
    environment queries against it. Returns how many materials were re-answered."""
    name = "Ruri Sky " + label
    image = _image(name, radiance(coefficients))
    world = bpy.data.worlds.get(name) or bpy.data.worlds.new(name)
    world.use_nodes = True
    tree = world.node_tree
    tree.nodes.clear()
    texture = tree.nodes.new("ShaderNodeTexEnvironment")
    texture.image = image
    texture.projection = "EQUIRECTANGULAR"
    background = tree.nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = 1.0
    output = tree.nodes.new("ShaderNodeOutputWorld")
    tree.links.new(texture.outputs["Color"], background.inputs["Color"])
    tree.links.new(background.outputs["Background"], output.inputs["Surface"])
    context.scene.world = world
    return material_builder.rewire_capabilities()
