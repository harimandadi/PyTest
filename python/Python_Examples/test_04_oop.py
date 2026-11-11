"""
04. OOP FOR FRAMEWORK DESIGN: classes, inheritance, abstraction, dunder methods, data classes.

Run:  python -m pytest python/Python_Examples/test_04_oop.py -v
The 4 pillars, in test-framework words:
  Encapsulation  BankAccount hides _balance; only deposit/withdraw change it
  Inheritance    LoginPage(BasePage) reuses open()
  Polymorphism   every Notifier has .send(); the caller never checks the type
  Abstraction    BasePage is abstract: you can't create one, only real pages
"""

from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from decimal import Decimal

import pytest


# ── 1. Encapsulation + custom exceptions: a ParaBank-style account ──────────────────────────
class InsufficientFundsError(Exception):
    pass


class BankAccount:
    interest_rate = Decimal("0.03")  # CLASS attribute: shared by all accounts

    def __init__(self, owner: str, balance: Decimal = Decimal("0")) -> None:
        self.owner = owner  # INSTANCE attribute
        self._balance = balance  # "_" = internal by convention

    @property  # read-only from outside: account.balance works, account.balance = 5 fails
    def balance(self) -> Decimal:
        return self._balance

    def deposit(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def withdraw(self, amount: Decimal) -> None:
        if amount > self._balance:
            raise InsufficientFundsError(f"balance {self._balance} < {amount}")
        self._balance -= amount

    def transfer_to(self, other: "BankAccount", amount: Decimal) -> None:
        self.withdraw(amount)  # if this raises, nothing is deposited: atomic enough here
        other.deposit(amount)

    def __repr__(self) -> str:  # what you see in pytest failure output
        return f"BankAccount(owner={self.owner!r}, balance={self._balance})"


@pytest.fixture
def accounts():
    return BankAccount("Asha", Decimal("100.00")), BankAccount("Ravi")


def test_transfer_moves_money(accounts):
    asha, ravi = accounts
    asha.transfer_to(ravi, Decimal("40.50"))
    assert (asha.balance, ravi.balance) == (Decimal("59.50"), Decimal("40.50"))  # Decimal: exact money


def test_overdraft_is_rejected_and_nothing_moves(accounts):
    asha, ravi = accounts
    with pytest.raises(InsufficientFundsError, match="100.00 < 500"):
        asha.transfer_to(ravi, Decimal("500"))
    assert ravi.balance == 0


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-5")])
def test_invalid_deposit(accounts, amount):
    with pytest.raises(ValueError):
        accounts[0].deposit(amount)


def test_balance_is_read_only(accounts):
    with pytest.raises(AttributeError):
        accounts[0].balance = Decimal("1000000")


# ── 2. Abstraction + inheritance: a BasePage the way frameworks use it ──────────────────────
class BasePage(ABC):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.visited: list[str] = []

    @property
    @abstractmethod
    def path(self) -> str:  # every page MUST say where it lives
        ...

    def open(self) -> "BasePage":  # shared behaviour, inherited
        self.visited.append(self.base_url + self.path)
        return self  # return self → fluent: LoginPage(url).open().login(...)


class LoginPage(BasePage):
    path = "/index.htm"

    def login(self, user: str) -> str:
        return f"logged in as {user}"


class TransferPage(BasePage):
    path = "/transfer.htm"


def test_abstract_class_cannot_be_instantiated():
    with pytest.raises(TypeError, match="abstract"):
        BasePage("http://x")  # type: ignore[abstract]


def test_inheritance_reuses_open():
    page = LoginPage("https://parabank.parasoft.com/parabank")
    assert page.open().login("john") == "logged in as john"
    assert page.visited == ["https://parabank.parasoft.com/parabank/index.htm"]
    assert isinstance(page, BasePage) and LoginPage.__mro__[1] is BasePage


# ── 3. Polymorphism: same method, different classes, no if/else on type ─────────────────────
class SlackNotifier:
    def send(self, summary: str) -> str:
        return f"slack: {summary}"


class EmailNotifier:
    def send(self, summary: str) -> str:
        return f"email: {summary}"


def notify_all(notifiers, summary: str) -> list[str]:
    return [n.send(summary) for n in notifiers]  # duck typing: anything with .send works


def test_polymorphism():
    assert notify_all([SlackNotifier(), EmailNotifier()], "3 failed") == ["slack: 3 failed", "email: 3 failed"]


# ── 4. Dataclasses + dunder methods: comparable, sortable test results ──────────────────────
@dataclass(order=True)  # order=True → <, > compare fields in order (priority first)
class Defect:
    priority: int
    title: str = field(compare=False)
    tags: list[str] = field(default_factory=list, compare=False)  # never `= []`


def test_dataclass_equality_and_sorting():
    defects = [Defect(3, "typo"), Defect(1, "login broken"), Defect(2, "slow page")]
    assert [d.title for d in sorted(defects)] == ["login broken", "slow page", "typo"]
    assert Defect(1, "a") == Defect(1, "b")  # title excluded from comparison
    assert Defect(1, "a").tags is not Defect(1, "b").tags  # each gets its own list


# ── 5. Classmethod factory + staticmethod ───────────────────────────────────────────────────
@dataclass
class User:
    username: str
    role: str

    @classmethod
    def admin(cls) -> "User":  # alternative constructor (factory)
        return cls("admin", "admin")

    @staticmethod
    def is_valid_username(name: str) -> bool:  # utility, needs no instance
        return name.isalnum() and 3 <= len(name) <= 20


def test_classmethod_and_staticmethod():
    assert User.admin() == User("admin", "admin")
    assert User.is_valid_username("qa_lead") is False and User.is_valid_username("qalead") is True


# ── 6. Data structures: Stack, Queue, LRU cache ─────────────────────────────────────────────
class Stack:
    def __init__(self) -> None:
        self._items: list = []

    def push(self, item) -> None:
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def __len__(self) -> int:  # enables len(stack) and `if stack:`
        return len(self._items)


class LRUCache:
    """Least Recently Used cache: classic design question. O(1) get/put with OrderedDict."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._data: OrderedDict = OrderedDict()

    def get(self, key):
        if key not in self._data:
            return None
        self._data.move_to_end(key)  # mark as recently used
        return self._data[key]

    def put(self, key, value) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)  # evict the least recently used


def test_stack_lifo():
    s = Stack()
    for step in ("open", "login", "transfer"):
        s.push(step)
    assert s.pop() == "transfer" and len(s) == 2
    with pytest.raises(IndexError):
        Stack().pop()


def test_lru_cache_evicts_least_recently_used():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")  # a is now most recent
    cache.put("c", 3)  # evicts b
    assert cache.get("b") is None and cache.get("a") == 1 and cache.get("c") == 3


# ── 7. Singleton (and why a module is usually enough) ───────────────────────────────────────
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.settings = {"env": "qa"}
        return cls._instance


def test_singleton():
    assert Config() is Config()
    # In Python, a module (config.py) is imported once, so it is already a singleton.
    # In pytest-xdist each worker is a process: one instance PER WORKER.
