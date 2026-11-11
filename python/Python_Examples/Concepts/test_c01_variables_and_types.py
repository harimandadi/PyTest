"""
C01 · BASIC · VARIABLES, TYPES, MUTABILITY, TRUTHINESS
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "A variable is a NAME TAG, not a box."
          `x = [1]` makes a list object and hangs the tag `x` on it. `y = x` hangs a SECOND
          tag on the SAME object. That one picture explains half of all Python bugs.

Run:  python -m pytest python/Python_Examples/Concepts/test_c01_variables_and_types.py -v
"""

import pytest


# ── 1. NAMES POINT TO OBJECTS ───────────────────────────────────────────────────────────────
# HOOK  "Two tags, one balloon": change the balloon through one tag, the other tag sees it.
def test_two_names_one_object():
    cart = ["Blue Top"]
    same_cart = cart  # NO copy: a second name tag on the same list
    same_cart.append("Jeans")
    assert cart == ["Blue Top", "Jeans"]  # cart "changed" too, it IS the same object
    assert id(cart) == id(same_cart)  # id() = the object's identity (its address in CPython)

    copy_cart = cart.copy()  # a NEW list → a new balloon
    copy_cart.append("Hat")
    assert "Hat" not in cart


# ── 2. MUTABLE vs IMMUTABLE ─────────────────────────────────────────────────────────────────
# HOOK  "LDS can change, the rest are frozen":  List, Dict, Set are MUTABLE;
#        int, float, str, bool, tuple, frozenset, None are IMMUTABLE.
# WHY (QA)  Shared mutable test data leaks between tests; immutable data can't.
def test_immutable_values_are_replaced_not_changed():
    name = "qa"
    original_id = id(name)
    name += "_lead"  # strings can't change: Python builds a NEW string and moves the tag
    assert name == "qa_lead"
    assert id(name) != original_id

    with pytest.raises(TypeError):
        "qa"[0] = "Q"  # type: ignore[index]  ← you cannot edit a string in place

    point = (1, 2)
    with pytest.raises(TypeError):
        point[0] = 5  # type: ignore[index]  ← tuples are frozen too


# ── 3. THE CORE TYPES AND CONVERSIONS ───────────────────────────────────────────────────────
# HOOK  "Convert at the DOOR": data from outside (UI text, env vars, CSV) is ALWAYS a str.
#        Convert once when it comes in, then work with real types.
def test_types_and_conversions():
    assert type(42) is int and type(4.2) is float and type("42") is str and type(True) is bool
    assert int("42") + 1 == 43  # "42" + 1 would be a TypeError: Python never guesses
    assert float("1,200.50".replace(",", "")) == 1200.50  # UI money text → number
    assert str(7) + " tests" == "7 tests"
    assert int(3.99) == 3  # int() TRUNCATES toward zero, it does not round
    assert round(2.5) == 2 and round(3.5) == 4  # "banker's rounding": .5 goes to the EVEN number
    assert 7 / 2 == 3.5 and 7 // 2 == 3 and 7 % 2 == 1 and 2**10 == 1024  # / // % **
    assert isinstance(True, int) and True + True == 2  # bool is a subclass of int!

    with pytest.raises(ValueError):
        int("12a")  # bad text → ValueError (wrong VALUE), not TypeError (wrong TYPE)


# ── 4. TRUTHINESS ───────────────────────────────────────────────────────────────────────────
# HOOK  "Empty and zero are False, everything else is True."
#        Falsy: False, None, 0, 0.0, "", [], {}, set(), ()
@pytest.mark.parametrize("value", [False, None, 0, 0.0, "", [], {}, set(), ()])
def test_falsy_values(value):
    assert not value


def test_truthiness_trap():
    assert bool("False") is True  # a NON-empty string is True, whatever it says!
    assert bool([0]) is True  # a list containing a zero is not empty
    # QA trap: env vars are strings → os.getenv("HEADLESS") == "false" is still truthy.
    headless = "false"
    assert (headless.lower() in ("1", "true", "yes")) is False  # parse it explicitly


# ── 5. None ─────────────────────────────────────────────────────────────────────────────────
# HOOK  "None means 'no value yet', and you test it with `is`."
def test_none():
    result = None
    assert result is None  # `is None`, never `== None`
    count = 0
    assert count is not None and not count  # 0 is a VALUE (falsy), None is NO value
    # So `if not count:` can't tell 0 from None; `if count is None:` can.


# ── 6. f-STRINGS ────────────────────────────────────────────────────────────────────────────
# HOOK  "f for format: put the expression in {curly braces}."
def test_f_strings():
    passed, total, env = 47, 50, "qa"
    assert f"{passed}/{total} passed on {env}" == "47/50 passed on qa"
    assert f"{passed / total:.1%}" == "94.0%"  # :.1% = percentage, 1 decimal
    assert f"{1234567.891:,.2f}" == "1,234,567.89"  # thousands separator, 2 decimals
    assert f"{'id':<5}|" == "id   |"  # pad to width 5, left-aligned (report tables)
    assert f"{env=}" == "env='qa'"  # = shows name AND value: perfect for debug prints


# ── 7. MULTIPLE ASSIGNMENT AND SWAP ─────────────────────────────────────────────────────────
# HOOK  "Right side is built FIRST, then unpacked into the left."
def test_swap_and_chained():
    a, b = 1, 2
    a, b = b, a  # builds (2, 1) first, then unpacks: no temp variable needed
    assert (a, b) == (2, 1)
    x = y = []  # ⚠ ONE list with two names (see section 1), not two lists
    x.append(1)
    assert y == [1]


"""
SELF-CHECK (answer out loud)
  1. y = x for a list, then y.append(1). What is x?               → changed: same object
  2. Which built-in types are mutable?                             → List, Dict, Set ("LDS")
  3. bool("False")?                                                → True (non-empty string)
  4. Why `is None` and not `== None`?                              → None is a single object;
                                                                     == can be overridden
  5. int(3.99), round(2.5)?                                        → 3, 2
"""
