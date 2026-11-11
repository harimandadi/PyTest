"""
C10 · INTERMEDIATE → ADVANCED · DATACLASSES, ENUMS, TYPE HINTS
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "@dataclass writes the boring parts for you": __init__, __repr__, __eq__ from a list
          of fields. Enum gives names to fixed choices. Type hints are LABELS a checker reads.

Run:  python -m pytest python/Python_Examples/Concepts/test_c10_dataclasses_enums_typing.py -v
"""

from dataclasses import FrozenInstanceError, asdict, dataclass, field, replace
from enum import Enum, IntEnum, StrEnum
from typing import Literal, Protocol, TypedDict, TypeVar

import pytest


# ── 1. DATACLASS BASICS ─────────────────────────────────────────────────────────────────────
# HOOK  "Fields in, free methods out."
@dataclass
class TestUser:
    __test__ = False  # not a pytest test class
    name: str
    email: str
    role: str = "user"  # fields WITH defaults must come after fields without
    tags: list[str] = field(default_factory=list)  # mutable default → default_factory, never []


def test_dataclass_basics():
    u = TestUser("Asha", "asha@example.com")
    assert repr(u) == "TestUser(name='Asha', email='asha@example.com', role='user', tags=[])"
    assert u == TestUser("Asha", "asha@example.com")  # __eq__ compares fields
    assert asdict(u)["role"] == "user"  # → dict, ready for json.dumps / API payloads
    assert TestUser("a", "b").tags is not TestUser("c", "d").tags  # each its own list


# ── 2. FROZEN + replace(): IMMUTABLE TEST DATA ──────────────────────────────────────────────
# HOOK  "frozen = laminated card": you can't edit it, you make a new copy with replace().
@dataclass(frozen=True)
class Env:
    name: str
    base_url: str
    workers: int = 2


def test_frozen_and_replace():
    qa = Env("qa", "https://qa.example")
    with pytest.raises(FrozenInstanceError):
        qa.workers = 8  # type: ignore[misc]
    local = replace(qa, name="local", workers=4)  # copy with changes
    assert (qa.workers, local.workers) == (2, 4)
    assert {qa: "ok"}[qa] == "ok"  # frozen dataclasses are hashable → usable as dict keys


# ── 3. __post_init__: VALIDATE ON CREATION ──────────────────────────────────────────────────
@dataclass
class Money:
    amount: float
    currency: str = "USD"

    def __post_init__(self) -> None:  # runs right after the generated __init__
        if self.amount < 0:
            raise ValueError("amount must be >= 0")
        self.currency = self.currency.upper()


def test_post_init():
    assert Money(5, "inr").currency == "INR"
    with pytest.raises(ValueError):
        Money(-1)


# ── 4. ENUMS: NAMED, FIXED CHOICES ──────────────────────────────────────────────────────────
# HOOK  "Enum = a dropdown in code": only the listed values exist, typos become errors.
class Status(StrEnum):  # StrEnum (3.11+): members ARE strings
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Priority(IntEnum):
    LOW = 1
    HIGH = 3


class Browser(Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"


def test_enums():
    assert Status("failed") is Status.FAILED  # look up by value
    assert Status.PASSED == "passed"  # StrEnum compares to plain strings
    assert [s.value for s in Status] == ["passed", "failed", "skipped"]  # iterate all
    assert Priority.HIGH > Priority.LOW  # IntEnum compares like numbers
    assert Browser["FIREFOX"].value == "firefox"  # look up by NAME
    with pytest.raises(ValueError):
        Status("passd")  # the typo is caught immediately


# ── 5. TYPE HINTS: THE VOCABULARY ───────────────────────────────────────────────────────────
# HOOK  "Hints are LABELS, not LOCKS": Python doesn't enforce them at runtime;
#        mypy / pyright / your IDE do. Validate OUTSIDE data with pydantic.
def find_user(users: list[TestUser], email: str) -> TestUser | None:  # X | None = "maybe X"
    return next((u for u in users if u.email == email), None)


Role = Literal["admin", "user"]  # only these exact strings


class ProductJson(TypedDict):  # the SHAPE of a dict (e.g. an API body)
    id: int
    name: str


class Sender(Protocol):  # "anything with a .send(str) -> str method" (structural typing)
    def send(self, message: str) -> str: ...


T = TypeVar("T")  # a generic: "whatever type comes in, the same type goes out"


def first_or_default(items: list[T], default: T) -> T:
    return items[0] if items else default


def test_type_hints():
    users = [TestUser("a", "a@x.com")]
    assert find_user(users, "a@x.com") is users[0] and find_user(users, "nope") is None
    product: ProductJson = {"id": 1, "name": "Blue Top"}
    assert product["name"] == "Blue Top"
    assert first_or_default([], "none") == "none" and first_or_default([3], 0) == 3
    role: Role = "admin"
    assert role in ("admin", "user")

    def double(n: int) -> int:
        return n * 2

    assert double("ab") == "abab"  # type: ignore[arg-type]  ← runs anyway: labels, not locks


"""
SELF-CHECK
  1. What does @dataclass generate?                     → __init__, __repr__, __eq__
  2. Mutable default in a dataclass?                    → field(default_factory=list)
  3. How do you "change" a frozen dataclass?            → dataclasses.replace(obj, x=...)
  4. Why enums instead of plain strings?                → typos fail fast; IDE autocomplete
  5. Are type hints checked when the code runs?         → no: a static checker uses them
"""
