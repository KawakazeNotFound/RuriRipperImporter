"""The one registry, for everything anything registers.

Before this there were fifteen pairs of ``register_x``/``unregister_x`` with a
module-level list behind each -- commands, panel sections, graph providers,
vertex stages, capability rewires, light-role refreshers, post stages, list
specs, mesh resolvers, detail rules. Every one of them had the same three
questions to answer and answered them slightly differently: what happens when
the same thing registers twice, what happens when a development reload
re-executes the module that declared it, and what happens when two different
modules claim one name.

So there is one answer here and no list anywhere else.

IDENTITY IS (declaring module, key). That is what tells a reload apart from a
collision: the same module declaring the same key again is the file on disk
having changed, and the new entry replaces the old one -- refusing it would
freeze the previous body in place while the source says otherwise.

A NAME is not the same thing as an identity, and only a name can collide. A
caller that STATES a key is claiming a name in the point's own namespace -- a
tab key, a command id, a section key -- and two modules claiming one of those is
two owners of one name, which is an error rather than a last-one-wins. A caller
that states none is identified by what it registered, and the qualified name of
a plain function is module-local by construction: two generated shading stacks
each own a ``refresh_main_light_role``, and they are two entries rather than one
collision. So the check runs on the stated key and on nothing else.

A point may state the capability an entry needs. Entries whose capability the
bound host does not answer are not registered-and-skipped: they are absent, so
nothing downstream has to remember to check.
"""

from __future__ import annotations

#: The points ARE process state. A development reload re-executes modules in
#: sys.modules order, which puts this one before every module that registers
#: into it -- so rebuilding the table here would wipe what the modules above had
#: just re-registered, and the sweep that wraps them would find nothing.
HOLDS_PROCESS_STATE = True


class Entry:
    """One registration: what was registered, who declared it, under what key."""

    __slots__ = ("value", "module", "key", "order")

    def __init__(self, value, module, key, order):
        self.value = value
        self.module = module
        self.key = key
        self.order = order

    def __repr__(self):
        return "<Entry {0}.{1}>".format(self.module, self.key)


def _module_of(value):
    return getattr(value, "__module__", "") or type(value).__module__


def _key_of(value):
    """What tells one registration apart from another within a module.

    A value that names itself answers for itself. A BOUND METHOD does not: five
    objects of one class registering their own ``provider`` all report the same
    qualified name, and folding them together would silently keep one and drop
    four -- which is exactly what happened to four of five generated shading
    stacks. So a bound method is identified by its OWNER as well, by whatever
    name that owner offers and by its object identity when it offers none."""
    named = _named(value)
    if named:
        return named
    owner = getattr(value, "__self__", None)
    qualified = getattr(value, "__qualname__", None) or type(value).__qualname__
    if owner is None:
        return qualified
    return "{0}@{1}".format(qualified, _named(owner) or hex(id(owner)))


def _named(value):
    for attribute in ("id", "name"):
        found = getattr(value, attribute, None)
        if isinstance(found, str) and found:
            return found
    return ""


class ExtensionPoint:
    """One named place things plug into.

    Registration order is preserved, because several of these are chains where
    the order a caller registered in is the order it meant (first claimant
    wins). Replacing an entry keeps its original position, so a reload does not
    reshuffle a chain.
    """

    __slots__ = ("name", "doc", "requires", "_entries", "_next")

    def __init__(self, name, doc="", requires=None):
        self.name = name
        self.doc = doc
        #: The capability protocol an entry presumes, or None when every host
        #: can hold one. Stated as the protocol CLASS, never a host name.
        self.requires = requires
        self._entries = {}
        self._next = 0

    def add(self, value, key=""):
        """Register ``value``, replacing what the same module filed under the
        same key. Returns the value, so a decorator form reads naturally."""
        from . import capabilities

        if self.requires is not None and capabilities.bound() \
                and not capabilities.supports(self.requires):
            return value
        identity = (_module_of(value), key or _key_of(value))
        existing = self._entries.get(identity)
        order = existing.order if existing is not None else self._next
        if existing is None:
            self._next += 1
        if key:
            taken = next((entry for entry in self._entries.values()
                          if entry.key == key and entry.module != identity[0]), None)
            if taken is not None:
                raise ValueError(
                    "two modules claim {0} entry {1!r}: {2} and {3}".format(
                        self.name, key, taken.module, identity[0]))
        self._entries[identity] = Entry(value, identity[0], identity[1], order)
        return value

    def remove(self, value, key=""):
        """Drop one registration. Silent when it is not there: an unregister
        that runs after a failed register must not raise over the first
        failure's shadow."""
        self._entries.pop((_module_of(value), key or _key_of(value)), None)

    def forget(self, module):
        """Drop everything one module declared -- what a module being unloaded
        (rather than reloaded) means."""
        for identity in [key for key in self._entries if key[0] == module]:
            del self._entries[identity]

    def clear(self):
        self._entries.clear()
        self._next = 0

    def entries(self):
        return sorted(self._entries.values(), key=lambda entry: entry.order)

    def get(self, key):
        """The value filed under ``key``, or None."""
        for entry in self.entries():
            if entry.key == key:
                return entry.value
        return None

    def keys(self):
        return tuple(entry.key for entry in self.entries())

    def __iter__(self):
        return iter(entry.value for entry in self.entries())

    def __len__(self):
        return len(self._entries)

    def __contains__(self, value):
        return any(entry.value is value for entry in self._entries.values())

    def __repr__(self):
        return "<ExtensionPoint {0} ({1})>".format(self.name, len(self._entries))


#: Every point, by name -- so a reload can sweep a module out of all of them at
#: once and a diagnostics panel can list what is plugged in anywhere without
#: importing whatever declared each point.
POINTS = {}


def point(name, doc="", requires=None):
    """Declare (or fetch) a point. Declaring it twice is a reload of the module
    that declared it, and the entries already in it are kept -- the point is a
    place, and re-executing the file that named it did not empty it."""
    found = POINTS.get(name)
    if found is None:
        found = POINTS[name] = ExtensionPoint(name, doc, requires)
    return found


def forget(module):
    """Sweep one module out of every point."""
    for entry in POINTS.values():
        entry.forget(module)
