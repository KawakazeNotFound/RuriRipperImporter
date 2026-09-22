"""The performances a selection states, on this host.

A clip arrives already re-anchored onto the target rig's own bone paths, so
there is nothing engine-specific left here -- which is why one module answers
for every title that ships animation.
"""

from __future__ import annotations


def import_animations(context, _bridge, package, options=None):
    """Build the performances ``package`` states onto the rig in front of us."""
    from . import packages as materialiser

    seeds = materialiser.seeds_of(package)
    if not seeds:
        return []
    built = materialiser.build_clips(context, "", seeds, None, options, activate=False)
    return list(range(built or 0))


def materialise(context, package, options=None):
    """A placement set: the same statement path everything else takes."""
    from . import packages as materialiser

    return materialiser.materialise(context, package, None, options)
