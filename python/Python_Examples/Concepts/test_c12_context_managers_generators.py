"""
C12 · ADVANCED · CONTEXT MANAGERS AND GENERATOR PIPELINES
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "with = a hotel stay": check-in (__enter__), your stay (the block), check-out
          (__exit__) happens even if you leave in a hurry (an exception).
          pytest's yield fixtures are the SAME idea: setup → yield → teardown.

Run:  python -m pytest python/Python_Examples/Concepts/test_c12_context_managers_generators.py -v
"""

import time
from contextlib import ExitStack, contextmanager, suppress

import pytest


# ── 1. CLASS-BASED CONTEXT MANAGER ──────────────────────────────────────────────────────────
# HOOK  "__enter__ opens, __exit__ closes; __exit__ returning True SWALLOWS the error."
class FakeDbConnection:
    def __init__(self, log: list[str]) -> None:
        self.log = log

    def __enter__(self) -> "FakeDbConnection":  # the value after `as`
        self.log.append("connect")
        return self

    def query(self, sql: str) -> list[dict]:
        if "DROP" in sql:
            raise PermissionError("not allowed in tests")
        return [{"id": 1}]

    def __exit__(self, exc_type, exc, tb) -> bool:  # gets error info, or three Nones
        self.log.append("rollback" if exc_type else "commit")
        self.log.append("disconnect")
        return False  # False = let the error propagate (almost always what you want)


def test_class_context_manager():
    log: list[str] = []
    with FakeDbConnection(log) as db:
        assert db.query("SELECT 1") == [{"id": 1}]
    assert log == ["connect", "commit", "disconnect"]

    log.clear()
    with pytest.raises(PermissionError):
        with FakeDbConnection(log) as db:
            db.query("DROP TABLE users")
    assert log == ["connect", "rollback", "disconnect"]  # cleaned up even on error


# ── 2. @contextmanager: THE SHORT WAY ───────────────────────────────────────────────────────
# HOOK  "Before yield = __enter__, after yield = __exit__", wrapped in try/finally.
@contextmanager
def timer(results: dict, name: str):
    start = time.perf_counter()
    try:
        yield  # the with-block runs here
    finally:
        results[name] = time.perf_counter() - start


@contextmanager
def temp_setting(settings: dict, key: str, value):
    old = settings.get(key)
    settings[key] = value
    try:
        yield settings
    finally:
        settings[key] = old  # restore even if the block failed


def test_contextmanager_decorator():
    timings: dict[str, float] = {}
    with timer(timings, "login"):
        sum(range(1000))
    assert timings["login"] >= 0

    settings = {"timeout": 30}
    with pytest.raises(RuntimeError):
        with temp_setting(settings, "timeout", 1):
            assert settings["timeout"] == 1
            raise RuntimeError("test failed")
    assert settings["timeout"] == 30  # restored


# ── 3. HANDY BUILT-INS: suppress, ExitStack ─────────────────────────────────────────────────
# HOOK  "suppress = a polite `except: pass` for ONE named error; ExitStack = a with-block for
#        a VARIABLE number of resources."
def test_suppress_and_exitstack():
    cleanup = {"a": 1}
    with suppress(KeyError):  # deleting something that may not exist
        del cleanup["missing"]

    log: list[str] = []
    with ExitStack() as stack:
        conns = [stack.enter_context(FakeDbConnection(log)) for _ in range(3)]
        assert len(conns) == 3
    assert log.count("disconnect") == 3  # all closed, in REVERSE order of opening


# ── 4. GENERATOR PIPELINES (lazy data processing) ───────────────────────────────────────────
# HOOK  "Pipes like Unix: each stage pulls ONE item from the previous, nothing is loaded whole."
#        read → parse → filter → take, and memory stays flat even for huge logs.
LOG_LINES = [
    "INFO login ok 120ms",
    "ERROR transfer failed 3400ms",
    "INFO logout ok 80ms",
    "ERROR billpay timeout 30000ms",
    "INFO search ok 95ms",
]


def read_lines(lines):
    for line in lines:  # in real life: `for line in open(path)`
        yield line


def parse(lines):
    for line in lines:
        level, action, *_, ms = line.split()
        yield {"level": level, "action": action, "ms": int(ms.removesuffix("ms"))}


def only(level, records):
    return (r for r in records if r["level"] == level)


def test_pipeline_is_lazy():
    pulled = []

    def spy(lines):
        for line in lines:
            pulled.append(line)
            yield line

    pipeline = only("ERROR", parse(spy(read_lines(LOG_LINES))))
    first_error = next(pipeline)
    assert first_error == {"level": "ERROR", "action": "transfer", "ms": 3400}
    assert len(pulled) == 2  # only read as far as needed: lines 1 and 2, not all 5
    assert [r["action"] for r in pipeline] == ["billpay"]  # continue where it paused


# ── 5. GENERATOR AS A CONTEXT: try/finally INSIDE a generator ───────────────────────────────
# HOOK  "Closing a generator runs its finally": that's why pytest yield-fixtures always tear down.
def fixture_like(log):
    log.append("setup")
    try:
        yield "resource"
    finally:
        log.append("teardown")


def test_generator_close_runs_finally():
    log: list[str] = []
    gen = fixture_like(log)
    assert next(gen) == "resource"  # pytest does this before the test…
    gen.close()  # …and this after it (passed OR failed)
    assert log == ["setup", "teardown"]


"""
SELF-CHECK
  1. What does __exit__ returning True do?               → swallows the exception
  2. In @contextmanager, where does the with-body run?   → at the yield
  3. Why wrap the yield in try/finally?                  → so cleanup runs if the body fails
  4. Benefit of a generator pipeline?                    → constant memory, stops early
  5. How is a pytest yield fixture like a context manager? → setup / yield / teardown
"""
