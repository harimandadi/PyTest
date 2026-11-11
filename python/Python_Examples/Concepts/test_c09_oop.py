"""
C09 · INTERMEDIATE · OBJECT-ORIENTED PYTHON
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "Class = cookie CUTTER, object = COOKIE, self = 'THIS cookie'."
          The class describes the shape once; every object is its own cookie with its own data.

Pillars, as a QA framework sees them ("A PIE"):
  Abstraction    hide the HOW behind a simple method (page.login(user))
  Polymorphism   same method name, different classes (every Notifier has .send)
  Inheritance    LoginPage IS-A BasePage, reuses open()
  Encapsulation  keep data private, change it only through methods

Run:  python -m pytest python/Python_Examples/Concepts/test_c09_oop.py -v
"""

from abc import ABC, abstractmethod

import pytest


# ── 1. CLASS, __init__, self, ATTRIBUTES ────────────────────────────────────────────────────
# HOOK  "__init__ is the BIRTH certificate": it fills in a new object's data.
#        "Class attribute = shared by ALL cookies; instance attribute = THIS cookie only."
class Browser:
    supported = ["chromium", "firefox", "webkit"]  # CLASS attribute (shared)
    launched_count = 0

    def __init__(self, name: str, headless: bool = True) -> None:
        if name not in Browser.supported:
            raise ValueError(f"unsupported browser {name}")
        self.name = name  # INSTANCE attributes (per object)
        self.headless = headless
        Browser.launched_count += 1  # change shared state via the CLASS name

    def describe(self) -> str:  # a METHOD: a function that receives the object as `self`
        mode = "headless" if self.headless else "headed"
        return f"{self.name} ({mode})"


def test_class_and_instance():
    before = Browser.launched_count
    chrome, fox = Browser("chromium"), Browser("firefox", headless=False)
    assert chrome.describe() == "chromium (headless)" and fox.describe() == "firefox (headed)"
    assert Browser.launched_count == before + 2  # shared counter
    assert chrome.supported is fox.supported  # same class-level list
    assert Browser.describe(chrome) == chrome.describe()  # ← what `self` really is
    with pytest.raises(ValueError):
        Browser("ie11")


# ── 2. ENCAPSULATION AND @property ──────────────────────────────────────────────────────────
# HOOK  "_single = 'please don't touch', __double = name-mangled, @property = a guarded door"
class Account:
    def __init__(self, balance: float = 0) -> None:
        self._balance = balance  # internal by convention

    @property
    def balance(self) -> float:  # read like an attribute: acct.balance (no parentheses)
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:  # every write goes through validation
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value


def test_property_guards_data():
    acct = Account(100)
    acct.balance = 50
    assert acct.balance == 50
    with pytest.raises(ValueError):
        acct.balance = -1


# ── 3. INHERITANCE, super(), OVERRIDING ─────────────────────────────────────────────────────
# HOOK  "Child IS-A parent: inherits everything, overrides what's different,
#        super() calls the parent's version."
class BasePage:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.history: list[str] = []

    def open(self, path: str = "/") -> str:
        url = self.base_url + path
        self.history.append(url)
        return url


class LoginPage(BasePage):
    def __init__(self, base_url: str, username_field: str = "#username") -> None:
        super().__init__(base_url)  # let the parent set ITS attributes first
        self.username_field = username_field

    def open(self, path: str = "/login") -> str:  # OVERRIDE: same name, new default
        url = super().open(path)  # reuse the parent's logic
        return url + " (login)"


def test_inheritance():
    page = LoginPage("https://bank.example")
    assert page.open() == "https://bank.example/login (login)"
    assert page.history == ["https://bank.example/login"]  # parent's attribute exists
    assert isinstance(page, BasePage) and issubclass(LoginPage, BasePage)


# ── 4. ABSTRACT BASE CLASSES ────────────────────────────────────────────────────────────────
# HOOK  "An abstract class is a CONTRACT": children MUST implement the abstract methods.
class Reporter(ABC):
    @abstractmethod
    def report(self, passed: int, failed: int) -> str: ...


class ConsoleReporter(Reporter):
    def report(self, passed: int, failed: int) -> str:
        return f"{passed} passed, {failed} failed"


class BrokenReporter(Reporter):  # forgot to implement report()
    pass


def test_abstract_contract():
    assert ConsoleReporter().report(9, 1) == "9 passed, 1 failed"
    with pytest.raises(TypeError):
        Reporter()  # type: ignore[abstract]  can't create the contract itself
    with pytest.raises(TypeError):
        BrokenReporter()  # type: ignore[abstract]  fails at CREATION, not later


# ── 5. POLYMORPHISM AND DUCK TYPING ─────────────────────────────────────────────────────────
# HOOK  "If it walks like a duck and quacks like a duck…": Python cares about METHODS, not family.
class JsonReporter:  # NOT a Reporter subclass, but has the same method
    def report(self, passed: int, failed: int) -> str:
        return f'{{"passed": {passed}, "failed": {failed}}}'


def test_duck_typing():
    outputs = [r.report(1, 0) for r in (ConsoleReporter(), JsonReporter())]
    assert outputs == ["1 passed, 0 failed", '{"passed": 1, "failed": 0}']


# ── 6. COMPOSITION OVER INHERITANCE ─────────────────────────────────────────────────────────
# HOOK  "HAS-A beats IS-A": a page HAS a menu; it isn't a kind of menu.
class AccountMenu:
    def items(self) -> list[str]:
        return ["Open New Account", "Accounts Overview", "Transfer Funds"]


class OverviewPage(BasePage):
    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)
        self.menu = AccountMenu()  # composed, reusable on every logged-in page


def test_composition():
    assert "Transfer Funds" in OverviewPage("x").menu.items()


# ── 7. DUNDER (MAGIC) METHODS ───────────────────────────────────────────────────────────────
# HOOK  "Dunders plug your class into Python's syntax": len(), ==, +, in, print, for…
class TestSuite:
    __test__ = False  # tells pytest: "not a test class" despite the name

    def __init__(self, name: str, tests: list[str] | None = None) -> None:
        self.name, self.tests = name, list(tests or [])

    def __len__(self) -> int:  # len(suite)
        return len(self.tests)

    def __contains__(self, test: str) -> bool:  # "login" in suite
        return test in self.tests

    def __iter__(self):  # for t in suite
        return iter(self.tests)

    def __add__(self, other: "TestSuite") -> "TestSuite":  # suite_a + suite_b
        return TestSuite(f"{self.name}+{other.name}", self.tests + other.tests)

    def __eq__(self, other: object) -> bool:  # suite_a == suite_b
        return isinstance(other, TestSuite) and self.tests == other.tests

    def __repr__(self) -> str:  # shown in pytest failure messages and the debugger
        return f"TestSuite({self.name!r}, {len(self)} tests)"


def test_dunder_methods():
    smoke, api = TestSuite("smoke", ["login"]), TestSuite("api", ["products"])
    merged = smoke + api
    assert len(merged) == 2 and "products" in merged and list(merged) == ["login", "products"]
    assert repr(merged) == "TestSuite('smoke+api', 2 tests)"
    assert TestSuite("a", ["x"]) == TestSuite("b", ["x"])


# ── 8. @classmethod AND @staticmethod ───────────────────────────────────────────────────────
# HOOK  "classmethod gets the CLASS (a factory); staticmethod gets NOTHING (a plain helper)."
class Credentials:
    def __init__(self, user: str, password: str) -> None:
        self.user, self.password = user, password

    @classmethod
    def from_string(cls, text: str) -> "Credentials":  # alternative constructor
        user, password = text.split(":", 1)
        return cls(user, password)

    @staticmethod
    def is_strong(password: str) -> bool:
        return len(password) >= 8 and any(c.isdigit() for c in password)


def test_classmethod_staticmethod():
    creds = Credentials.from_string("john:demo:123")
    assert (creds.user, creds.password) == ("john", "demo:123")  # split ONCE
    assert Credentials.is_strong("passw0rd!") and not Credentials.is_strong("short1")


# ── 9. MRO: WHO WINS IN MULTIPLE INHERITANCE ────────────────────────────────────────────────
# HOOK  "Left to right, children before parents" (the C3 linearisation).
class Loggable:
    def tag(self) -> str:
        return "log"


class Screenshotting:
    def tag(self) -> str:
        return "shot"


class SmartPage(Loggable, Screenshotting):
    pass


def test_mro():
    assert SmartPage().tag() == "log"  # Loggable is listed first
    assert [c.__name__ for c in SmartPage.__mro__] == ["SmartPage", "Loggable", "Screenshotting", "object"]


"""
SELF-CHECK
  1. What is `self`?                                   → the object the method was called on
  2. Class vs instance attribute?                      → shared by all vs per object
  3. Why super().__init__()?                           → so the parent sets up its part
  4. When does an incomplete ABC subclass fail?        → when you try to create an instance
  5. HAS-A or IS-A for a page with a menu?             → HAS-A (composition)
"""
