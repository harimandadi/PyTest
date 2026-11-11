"""
C07 · INTERMEDIATE · EXCEPTIONS: try / except / else / finally, custom errors, raise from
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "TRY the risky thing, EXCEPT catch what you EXPECT, ELSE celebrate,
           FINALLY clean up no matter what."   →  T-E-E-F: "Try Every Exit Finally"

Run:  python -m pytest python/Python_Examples/Concepts/test_c07_exceptions.py -v
"""

import json

import pytest


# ── 1. THE FULL try STATEMENT ───────────────────────────────────────────────────────────────
def parse_body(text: str, log: list[str]) -> dict | None:
    try:
        data = json.loads(text)  # risky: may raise json.JSONDecodeError
    except json.JSONDecodeError as error:  # catch the SPECIFIC error you expect
        log.append(f"bad json at pos {error.pos}")
        return None
    else:  # runs only if NO exception happened
        log.append("parsed")
        return data
    finally:  # runs ALWAYS: success, failure, even after return
        log.append("closed")


def test_try_except_else_finally():
    log: list[str] = []
    assert parse_body('{"ok": true}', log) == {"ok": True}
    assert log == ["parsed", "closed"]

    log.clear()
    assert parse_body("{oops", log) is None
    assert log == ["bad json at pos 1", "closed"]  # finally ran even after `return None`


# ── 2. THE COMMON EXCEPTION TYPES ───────────────────────────────────────────────────────────
# HOOK  "Name the problem": wrong TYPE → TypeError, right type wrong VALUE → ValueError,
#        no such KEY → KeyError, no such INDEX → IndexError, no such ATTRIBUTE → AttributeError
@pytest.mark.parametrize(
    "action, error",
    [
        (lambda: "1" + 1, TypeError),
        (lambda: int("abc"), ValueError),
        (lambda: {}["missing"], KeyError),
        (lambda: [][0], IndexError),
        (lambda: None.text, AttributeError),  # the classic "element not found" follow-up
        (lambda: 1 / 0, ZeroDivisionError),
        (lambda: open("no/such/file.txt"), FileNotFoundError),
    ],
)
def test_common_exceptions(action, error):
    with pytest.raises(error):
        action()


# ── 3. CUSTOM EXCEPTIONS (a small hierarchy) ────────────────────────────────────────────────
# HOOK  "Your own error names make failures SEARCHABLE": catch the family or one member.
class FrameworkError(Exception):
    """Base for everything our framework raises."""


class ConfigError(FrameworkError):
    pass


class ApiContractError(FrameworkError):
    def __init__(self, endpoint: str, field: str) -> None:
        super().__init__(f"{endpoint}: field '{field}' missing")  # sets the message
        self.endpoint, self.field = endpoint, field  # extra data for reports


def check_contract(body: dict) -> None:
    if "price" not in body:
        raise ApiContractError("/productsList", "price")


def test_custom_exceptions():
    with pytest.raises(ApiContractError, match="field 'price' missing") as info:
        check_contract({"id": 1})
    assert info.value.field == "price"

    with pytest.raises(FrameworkError):  # catching the PARENT also catches children
        check_contract({})


# ── 4. raise ... from: KEEP THE CAUSE ───────────────────────────────────────────────────────
# HOOK  "from = the paper trail": the new error remembers the original one.
def load_env(name: str) -> str:
    environments = {"qa": "https://qa.example"}
    try:
        return environments[name]
    except KeyError as error:
        raise ConfigError(f"unknown env {name!r}; use one of {list(environments)}") from error


def test_raise_from():
    with pytest.raises(ConfigError) as info:
        load_env("prd")
    assert isinstance(info.value.__cause__, KeyError)  # traceback shows BOTH errors


# ── 5. RE-RAISE AFTER LOGGING ───────────────────────────────────────────────────────────────
# HOOK  "Bare `raise` passes the SAME error on, with its original traceback."
def test_reraise():
    seen = []
    with pytest.raises(ValueError, match="bad"):
        try:
            raise ValueError("bad")
        except ValueError:
            seen.append("logged")
            raise  # don't swallow it
    assert seen == ["logged"]


# ── 6. EAFP vs LBYL ─────────────────────────────────────────────────────────────────────────
# HOOK  "EAFP = Easier to Ask Forgiveness than Permission" (Pythonic: just try it).
#        "LBYL = Look Before You Leap" (check first). Both are fine; EAFP avoids race conditions.
def price_eafp(product: dict) -> str:
    try:
        return product["price"]
    except KeyError:
        return "n/a"


def price_lbyl(product: dict) -> str:
    return product["price"] if "price" in product else "n/a"


def test_eafp_and_lbyl_agree():
    for p in ({"price": "Rs. 500"}, {}):
        assert price_eafp(p) == price_lbyl(p)


# ── 7. WHAT NOT TO DO ───────────────────────────────────────────────────────────────────────
# HOOK  "Never `except: pass`": it swallows EVERYTHING, including the AssertionError
#        that was supposed to fail your test.
def swallow_everything():
    try:
        assert 1 == 2, "this test should fail"
    except Exception:  # noqa: BLE001  ← the bug
        pass
    return "looks green"


def test_swallowing_hides_failures():
    assert swallow_everything() == "looks green"  # a real failure became a pass. Dangerous!


# ── 8. EXCEPTION GROUPS (3.11+): several failures at once ───────────────────────────────────
# HOOK  "except* catches by TYPE inside a group" (used by asyncio.TaskGroup, soft asserts).
def test_exception_group():
    caught = []
    try:
        raise ExceptionGroup("2 checks failed", [ValueError("price"), KeyError("id")])
    except* ValueError as group:
        caught.append(len(group.exceptions))
    except* KeyError:
        caught.append("key")
    assert caught == [1, "key"]


"""
SELF-CHECK
  1. When does `else` in try run?                  → only if no exception was raised
  2. Does `finally` run after `return`?            → yes, always
  3. int("abc") raises?                            → ValueError (wrong value, right type)
  4. Why `raise X from e`?                         → keeps the original cause in the traceback
  5. Why is `except Exception: pass` bad in tests? → it hides AssertionError → false passes
"""
