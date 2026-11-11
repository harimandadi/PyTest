"""
C14 · ADVANCED · PYTHON INTERNALS AND PERFORMANCE
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "Everything is an object, every object has a TYPE, an ID and a REFCOUNT."
          Knowing how Python stores things explains hashing, copying, and why some code is slow.

Run:  python -m pytest python/Python_Examples/Concepts/test_c14_internals_and_performance.py -v
"""

import gc
import sys
import timeit
import weakref

import pytest


# ── 1. EVERYTHING IS AN OBJECT ──────────────────────────────────────────────────────────────
# HOOK  "Even 5, len and a class are objects with a type."
def test_everything_is_an_object():
    assert type(5) is int and type(len).__name__ == "builtin_function_or_method"
    assert type(int) is type  # classes are objects whose type is `type`
    assert isinstance(None, object) and isinstance(int, object)


# ── 2. REFERENCE COUNTING AND GARBAGE COLLECTION ────────────────────────────────────────────
# HOOK  "Count the tags: when no name points to an object, it's freed.
#        Cycles (a → b → a) need the gc, the cleanup crew."
class Node:
    pass


def test_refcount_and_cycles():
    data = []
    before = sys.getrefcount(data)  # includes the temporary reference made by the call
    alias = data
    assert sys.getrefcount(data) == before + 1
    del alias  # removes a TAG, not the object
    assert sys.getrefcount(data) == before

    a, b = Node(), Node()
    a.other, b.other = b, a  # a reference CYCLE: refcounts never reach 0 on their own
    watcher = weakref.ref(a)  # a weak reference doesn't keep the object alive
    del a, b
    gc.collect()  # the cycle collector finds and frees them
    assert watcher() is None


# ── 3. HASHING: WHY DICT KEYS MUST BE IMMUTABLE ─────────────────────────────────────────────
# HOOK  "A dict is a WAREHOUSE with numbered shelves: hash(key) picks the shelf.
#        If the key could change, its shelf number would change and you'd never find it again."
def test_hashing():
    assert hash("login") == hash("login")  # same value → same shelf (within one run)
    assert hash((1, 2)) == hash((1, 2))
    with pytest.raises(TypeError, match="unhashable"):
        hash([1, 2])  # lists can change → not hashable
    assert {1: "a", 1.0: "b"} == {1: "b"}  # 1 == 1.0 and same hash → SAME key


# ── 4. == vs is, AND SMALL-OBJECT CACHING ───────────────────────────────────────────────────
# HOOK  "`is` = same OBJECT, `==` = same VALUE. Use `is` ONLY for None, True, False."
def test_identity_vs_equality():
    a = [1, 2]
    b = [1, 2]
    assert a == b and a is not b
    x = int("1000")  # built at runtime → two distinct int objects…
    y = int("1000")
    assert x == y  # …equal values. `x is y` is False in CPython: never rely on `is` for numbers


# ── 5. COMPLEXITY OF THE BUILT-IN STRUCTURES ────────────────────────────────────────────────
# HOOK  "Lookups: dict/set are O(1) (one shelf), list is O(n) (check every item)."
def test_set_lookup_beats_list_lookup():
    items = list(range(50_000))
    as_set = set(items)
    t_list = timeit.timeit(lambda: 49_999 in items, number=50)
    t_set = timeit.timeit(lambda: 49_999 in as_set, number=50)
    assert t_set < t_list  # thousands of times faster at this size


"""
   Operation                          list        dict / set
   x in c                             O(n)        O(1)
   append / add                       O(1)        O(1)
   insert(0, x) / pop(0)              O(n)        –          (use collections.deque: O(1))
   get by index / key                 O(1)        O(1)
   sort                               O(n log n)  –
"""


# ── 6. __slots__: SMALLER, STRICTER OBJECTS ─────────────────────────────────────────────────
# HOOK  "__slots__ = fixed seats": no per-object __dict__, less memory, no typo attributes.
class PointSlots:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y


def test_slots():
    p = PointSlots(1, 2)
    with pytest.raises(AttributeError):
        p.z = 3  # type: ignore[attr-defined]  typo-proof: can't add new attributes
    assert not hasattr(p, "__dict__")


# ── 7. ATTRIBUTE LOOKUP HOOKS: __getattr__ ──────────────────────────────────────────────────
# HOOK  "__getattr__ is the LAST CHANCE desk": called only when normal lookup fails.
class Locators:
    _map = {"login_button": "#loginBtn", "username": "input[name=username]"}

    def __getattr__(self, name: str) -> str:
        try:
            return self._map[name]
        except KeyError:
            raise AttributeError(f"no locator named {name!r}") from None


def test_getattr():
    loc = Locators()
    assert loc.login_button == "#loginBtn"
    with pytest.raises(AttributeError, match="logn_button"):
        loc.logn_button


# ── 8. DESCRIPTORS (how @property works underneath) ─────────────────────────────────────────
# HOOK  "A descriptor is a SMART attribute that lives on the class and guards every get/set."
class Positive:
    def __set_name__(self, owner, name):  # learns its own attribute name
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.private[1:]} must be > 0")
        setattr(obj, self.private, value)


class Timeouts:
    page_load = Positive()  # reusable validation for MANY attributes
    api = Positive()

    def __init__(self, page_load: int, api: int) -> None:
        self.page_load, self.api = page_load, api


def test_descriptor():
    t = Timeouts(30, 10)
    assert t.page_load == 30
    with pytest.raises(ValueError, match="api must be > 0"):
        t.api = 0


# ── 9. MEASURE, DON'T GUESS ─────────────────────────────────────────────────────────────────
# HOOK  "Profile first, optimise second": timeit for snippets, cProfile for whole runs,
#        pytest --durations=10 for the slowest tests.
def test_join_vs_concat_measured():
    def concat():
        s = ""
        for i in range(500):
            s += str(i)
        return s

    def join():
        return "".join(str(i) for i in range(500))

    assert concat() == join()  # same result; join is the idiom for big strings


"""
SELF-CHECK
  1. When is an object freed?                         → refcount hits 0, or gc finds it in a cycle
  2. Why can't a list be a dict key?                  → mutable → unhashable
  3. `x in my_set` vs `x in my_list` complexity?      → O(1) vs O(n)
  4. What do __slots__ buy you?                       → less memory, no accidental attributes
  5. When is __getattr__ called?                      → only when normal lookup fails
"""
