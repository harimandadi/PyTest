"""
C04 · BASIC → INTERMEDIATE · FUNCTIONS: parameters, defaults, *args/**kwargs, scope, lambda
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "A function is a recipe: parameters are the ingredients, return is the dish.
           No return line? You get None."

Run:  python -m pytest python/Python_Examples/Concepts/test_c04_functions.py -v
"""

import pytest


# ── 1. DEFINE, CALL, RETURN ─────────────────────────────────────────────────────────────────
# HOOK  "print SHOWS, return GIVES": only return hands a value back to the caller.
def add(a: int, b: int) -> int:
    return a + b


def log_only(a: int) -> None:
    _ = a * 2  # computes but never returns


def min_max(values: list[int]) -> tuple[int, int]:
    return min(values), max(values)  # "multiple returns" = ONE tuple, unpacked by the caller


def test_return_values():
    assert add(2, 3) == 5
    assert log_only(1) is None  # no return statement → None
    low, high = min_max([4, 1, 9])
    assert (low, high) == (1, 9)


# ── 2. POSITIONAL, KEYWORD, DEFAULT ─────────────────────────────────────────────────────────
# HOOK  "Keywords are labels on the ingredients": order stops mattering and calls explain themselves.
def create_user(name: str, role: str = "user", active: bool = True) -> dict:
    return {"name": name, "role": role, "active": active}


def test_positional_keyword_default():
    assert create_user("Asha") == {"name": "Asha", "role": "user", "active": True}  # defaults
    assert create_user("Ravi", active=False)["active"] is False  # skip role, set active
    assert create_user(role="admin", name="Root")["role"] == "admin"  # any order by keyword
    with pytest.raises(TypeError):
        create_user()  # type: ignore[call-arg]  missing required `name`


# ── 3. THE MUTABLE DEFAULT TRAP ─────────────────────────────────────────────────────────────
# HOOK  "Defaults are baked ONCE, when `def` runs" → a list default is shared by every call.
def append_bad(item, bucket=[]):  # noqa: B006
    bucket.append(item)
    return bucket


def append_good(item, bucket=None):
    bucket = [] if bucket is None else bucket  # fresh list per call
    bucket.append(item)
    return bucket


def test_mutable_default():
    append_bad(1)
    assert append_bad(2) == [1, 2]  # ← surprise: 1 survived from the previous call
    append_good(1)
    assert append_good(2) == [2]


# ── 4. *args AND **kwargs ───────────────────────────────────────────────────────────────────
# HOOK  "* packs a TUPLE, ** packs a DICT" (in a def). In a CALL, they UNPACK.
def build_url(base: str, *parts: str, **query: str) -> str:
    url = "/".join([base.rstrip("/"), *parts])
    if query:
        url += "?" + "&".join(f"{k}={v}" for k, v in query.items())
    return url


def test_args_kwargs():
    assert build_url("https://api", "products", "1") == "https://api/products/1"
    assert build_url("https://api/", "search", q="top", page="2") == "https://api/search?q=top&page=2"
    parts, params = ["brands"], {"page": "1"}
    assert build_url("https://api", *parts, **params) == "https://api/brands?page=1"


# ── 5. KEYWORD-ONLY AND POSITIONAL-ONLY ─────────────────────────────────────────────────────
# HOOK  "After * = must say the name.  Before / = must NOT say the name."
def transfer(amount: float, /, *, from_id: int, to_id: int) -> str:
    return f"{amount} from {from_id} to {to_id}"


def test_keyword_only():
    assert transfer(100, from_id=1, to_id=2) == "100 from 1 to 2"
    with pytest.raises(TypeError):
        transfer(100, 1, 2)  # type: ignore[misc]  ids MUST be named: no mixing up from/to!


# ── 6. SCOPE: LEGB ──────────────────────────────────────────────────────────────────────────
# HOOK  "LEGB = Local → Enclosing → Global → Built-in": the order Python searches for a name.
ENV = "qa"  # Global


def test_legb_scope():
    def outer():
        env = "staging"  # Enclosing (for inner)

        def inner():
            return env  # not Local → found in Enclosing

        return inner()

    assert outer() == "staging"
    assert ENV == "qa"  # the global was never touched
    assert len("abc") == 3  # `len` is found in Built-in


def test_nonlocal_and_global():
    counter = 0

    def increment():
        nonlocal counter  # "I mean the ENCLOSING counter, not a new local one"
        counter += 1

    increment()
    increment()
    assert counter == 2
    # `global X` does the same for module-level names. In framework code avoid both:
    # return values or use an object instead. Hidden shared state = flaky tests.


# ── 7. LAMBDA: a one-line, nameless function ────────────────────────────────────────────────
# HOOK  "lambda = a function on a sticky note": for short `key=` arguments, nothing more.
def test_lambda_as_sort_key():
    tests = [("login", 1.2), ("transfer", 3.4), ("logout", 0.3)]
    assert [n for n, _ in sorted(tests, key=lambda t: t[1], reverse=True)] == ["transfer", "login", "logout"]
    assert max(tests, key=lambda t: t[1])[0] == "transfer"


# ── 8. FUNCTIONS ARE OBJECTS ────────────────────────────────────────────────────────────────
# HOOK  "Functions are values": store them in dicts, pass them around (see C13 for more).
def test_dispatch_table():
    actions = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b}  # replaces an if/elif chain
    assert actions["sub"](10, 4) == 6


# ── 9. DOCSTRINGS AND TYPE HINTS ────────────────────────────────────────────────────────────
def percentage(part: int, whole: int) -> float:
    """Return part/whole as a percentage. Raises ZeroDivisionError if whole is 0."""
    return 100 * part / whole


def test_docstring_and_hints():
    assert "percentage" in percentage.__doc__.lower()
    assert percentage.__annotations__["return"] in (float, "float")
    with pytest.raises(ZeroDivisionError):
        percentage(1, 0)


"""
SELF-CHECK
  1. What does a function without `return` give back?     → None
  2. def f(x, items=[]) — what goes wrong?                 → the list is shared across calls
  3. *args is a ___, **kwargs is a ___                      → tuple, dict
  4. What does LEGB stand for?                              → Local, Enclosing, Global, Built-in
  5. Why make parameters keyword-only?                      → calls can't silently swap them
"""
