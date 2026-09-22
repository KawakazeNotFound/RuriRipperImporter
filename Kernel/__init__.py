"""The host-neutral application core.

Nothing under this package may import a host API -- no ``bpy``, no
``substance_painter``, no widget toolkit, and no game's name. What a host can do
is the protocols of :mod:`Kernel.host` its driver derives from, and what a host is
asked to do arrives as DATA the host then materialises. The rule is mechanically
checkable: ``Kernel/**`` grepped for those names must come back empty.

Inside, each of these is stated exactly once:

``bridge/``          the reader, reached through four verbs and nothing else (a
                     table, bytes, a view, a search) plus session control.
``statement.py``     the one place those bytes become arrays -- the only
                     ``frombuffer`` in the package.
``app/loading.py``   the one load: seeds in, the host's own objects out.
``app/layout.py``    the one panel vocabulary, and every surface it opens by id.
``extensions.py``    the one registry anything plugs into.
``options.py``       the one table of import options, which both hosts draw from.

The layer ABOVE is ``Host/<name>`` -- one driver per application, the only place
that application's API appears, and the only place that answers what it can do
(by DERIVING from the protocols it can honour). The layer BESIDE is
``Game/<name>`` -- the panels a game adds, which call the kernel and hold no
logic of their own, and the generated shader stack for each host. What a game
IS, and what a seed of it loads as, the reader answers.
"""
