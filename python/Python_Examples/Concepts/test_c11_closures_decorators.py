"""
C11 · ADVANCED · FIRST-CLASS FUNCTIONS, CLOSURES, DECORATORS, functools
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "A decorator is GIFT WRAP": the gift (your function) is unchanged; the wrapping adds
          something around it (timing, retry, logging). @deco on top = func = deco(func).

Learn in this order: functions are values → closures → decorators → decorators with arguments.

Run:  python -m pytest python/Python_Examples/Concepts/test_c11_closures_decorators.py -v
"""

import functools
import time

import pytest


# ── 1. FUNCTIONS ARE VALUES (first-class) ───────────────────────────────────────────────────
# HOOK  "No parentheses = the function itself; parentheses = CALL it."
def shout(text: str) -> str:
    return text.upper()


def apply(func, value):  # a HIGHER-ORDER function: takes a function as input
    return func(value)


def test_functions_are_values():
    f = shout  # no () → the function object
    assert f("hi") == "HI" and apply(shout, "qa") == "QA"
    assert list(map(str.strip, [" a ", "b "])) == ["a", "b"]
    assert list(filter(lambda n: n > 1, [0, 1, 2, 3])) == [2, 3]  # comprehensions are usually clearer
    assert functools.reduce(lambda acc, n: acc + n, [1, 2, 3], 0) == 6


# ── 2. CLOSURES ─────────────────────────────────────────────────────────────────────────────
# HOOK  "A closure is a function with a BACKPACK": it carries variables from where it was born.
def make_url_builder(base_url: str):
    def build(path: str) -> str:
        return base_url + path  # base_url lives in the backpack
    return build


def make_counter():
    count = 0

    def increment() -> int:
        nonlocal count  # modify the backpack variable (not create a local)
        count += 1
        return count

    return increment


def test_closures():
    qa, prod = make_url_builder("https://qa.example"), make_url_builder("https://example.com")
    assert qa("/login") == "https://qa.example/login" and prod("/login") == "https://example.com/login"
    counter = make_counter()
    counter()
    assert counter() == 2  # state kept between calls without a class or a global


def test_late_binding_trap():
    # HOOK  "Closures remember the VARIABLE, not the value at that moment."
    funcs = [lambda: i for i in range(3)]
    assert [f() for f in funcs] == [2, 2, 2]  # all see the FINAL i
    fixed = [lambda i=i: i for i in range(3)]  # default arg captures the value NOW
    assert [f() for f in fixed] == [0, 1, 2]


# ── 3. A DECORATOR FROM SCRATCH ─────────────────────────────────────────────────────────────
# HOOK  "Decorator recipe: take func → define wrapper(*args, **kwargs) → do extra → call func
#        → return wrapper."  And ALWAYS @functools.wraps(func).
def timed(func):
    @functools.wraps(func)  # copies __name__/__doc__ so reports and debuggers stay correct
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            wrapper.last_duration = time.perf_counter() - start  # attach data to the wrapper

    wrapper.last_duration = 0.0
    return wrapper


@timed  # same as: login = timed(login)
def login(user: str) -> str:
    """Log a user in."""
    return f"welcome {user}"


def test_decorator_basics():
    assert login("john") == "welcome john"
    assert login.__name__ == "login" and login.__doc__ == "Log a user in."  # wraps did that
    assert login.last_duration >= 0


# ── 4. DECORATOR WITH ARGUMENTS (three layers) ──────────────────────────────────────────────
# HOOK  "Arguments need ONE MORE LAYER": retry(3) RETURNS the decorator, which wraps the func.
#        factory(args) → decorator(func) → wrapper(*args, **kwargs)
def retry(times: int, exceptions: tuple = (AssertionError,), delay: float = 0.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise  # out of attempts: the ORIGINAL error
                    time.sleep(delay)

        return wrapper

    return decorator


def test_decorator_with_arguments():
    calls = []

    @retry(times=3)
    def flaky_check():
        calls.append(1)
        assert len(calls) >= 2, "not yet"
        return "ok"

    assert flaky_check() == "ok" and len(calls) == 2

    @retry(times=2)
    def always_fails():
        raise AssertionError("down")

    with pytest.raises(AssertionError, match="down"):
        always_fails()


# ── 5. STACKING DECORATORS ──────────────────────────────────────────────────────────────────
# HOOK  "Closest to the function wraps FIRST" (bottom-up), runs OUTSIDE-IN.
def tag(label):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*a, **k):
            return f"<{label}>{func(*a, **k)}</{label}>"
        return wrapper
    return decorator


@tag("b")  # applied second (outer)
@tag("i")  # applied first (inner)
def title() -> str:
    return "Report"


def test_stacking_order():
    assert title() == "<b><i>Report</i></b>"


# ── 6. BUILT-IN DECORATORS FROM functools ───────────────────────────────────────────────────
# HOOK  "cache remembers answers; partial pre-fills arguments."
call_log = []


@functools.cache  # same inputs → stored result, the body runs once per input
def load_config(env: str) -> dict:
    call_log.append(env)
    return {"env": env}


def test_cache_and_partial():
    load_config("qa")
    load_config("qa")
    assert call_log == ["qa"]  # second call came from the cache
    assert load_config.cache_info().hits == 1

    to_int_from_binary = functools.partial(int, base=2)  # pre-filled keyword
    assert to_int_from_binary("1010") == 10


# ── 7. CLASS DECORATOR / DECORATING A CLASS ─────────────────────────────────────────────────
# HOOK  "A decorator can take a CLASS too": register pages, add behaviour.
PAGES: dict[str, type] = {}


def register(cls):
    PAGES[cls.__name__] = cls  # a plugin registry, no if/elif needed
    return cls  # return the class unchanged


@register
class CheckoutPage:
    pass


def test_class_registry():
    assert PAGES["CheckoutPage"] is CheckoutPage


"""
SELF-CHECK
  1. What does @timed above def f do?                  → f = timed(f)
  2. Why @functools.wraps?                             → keeps name/doc of the original
  3. How many nested functions for @retry(3)?          → three: factory → decorator → wrapper
  4. Two decorators: which is applied first?           → the one closest to the function
  5. Closures remember values or variables?            → variables (late binding)
"""
