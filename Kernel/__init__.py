"""The host-neutral application core.

Nothing under this package may import a host API -- no ``bpy``, no
``substance_painter``, no widget toolkit, and no game's name. What a host can do
is asked for through :mod:`Kernel.capabilities`, and what a host is asked to do
arrives as DATA the host then materialises. The rule is mechanically checkable:
``Kernel/**`` grepped for those names must come back empty.

Inside, four things are each stated exactly once:

``bridge/``       the reader, reached through four verbs and nothing else (a
                  table, bytes, a view, a search) plus session control.
``statement.py``  the one place those bytes become arrays -- the only
                  ``frombuffer`` in the package.
``extensions.py`` the one registry anything plugs into.
``options.py``    the one table of import options, which both hosts draw from.

The layer ABOVE is ``Host/<name>`` -- one driver per application, the only place
that application's API appears, and the only place that answers what it can do
(by DERIVING from the protocols it can honour). The layer BESIDE is
``Game/<name>`` -- data only: the generated shader stack for each host, and the
texture-role layer that says what that game's property names mean. What a game
IS, the reader answers.
"""
