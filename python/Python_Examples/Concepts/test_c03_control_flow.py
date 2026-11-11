"""
C03 · BASIC · CONTROL FLOW: if, for, while, break/continue, loop-else, match
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "Indentation IS the block." No braces: the code that belongs to an if/for is the
          code indented under it. 4 spaces, always.

Run:  python -m pytest python/Python_Examples/Concepts/test_c03_control_flow.py -v
"""

import pytest


# ── 1. if / elif / else ─────────────────────────────────────────────────────────────────────
# HOOK  "First True wins": Python checks top-down and runs ONLY the first matching branch.
def grade(pass_rate: float) -> str:
    if pass_rate >= 95:
        return "green"
    elif pass_rate >= 80:  # only reached if the first condition was False
        return "amber"
    else:
        return "red"


@pytest.mark.parametrize("rate, colour", [(100, "green"), (95, "green"), (94.9, "amber"), (80, "amber"), (0, "red")])
def test_grade_boundaries(rate, colour):  # QA instinct: test AT and AROUND each boundary
    assert grade(rate) == colour


def test_conditional_expression_and_chaining():
    status = "pass" if 3 > 2 else "fail"  # one-line if: X if condition else Y
    assert status == "pass"
    age = 25
    assert 18 <= age < 60  # chained comparison = (18 <= age) and (age < 60)


# ── 2. and / or SHORT-CIRCUIT ───────────────────────────────────────────────────────────────
# HOOK  "`or` stops at the first TRUTHY, `and` stops at the first FALSY" and returns THAT value.
def test_short_circuit():
    assert ("" or "default") == "default"  # common: value or fallback
    assert (0 or None or "x") == "x"
    assert ("a" and "b") == "b"  # all truthy → returns the LAST
    user = None
    assert (user and user.name) is None  # safe: user.name never evaluated


# ── 3. for LOOPS: iterate over THINGS, not indexes ──────────────────────────────────────────
# HOOK  "for item in items" reads like English. Need the index too? enumerate. Two lists? zip.
def test_for_loops():
    browsers = ["chromium", "firefox", "webkit"]
    seen = []
    for i, name in enumerate(browsers, start=1):  # (1, 'chromium'), (2, 'firefox')…
        seen.append(f"{i}:{name}")
    assert seen == ["1:chromium", "2:firefox", "3:webkit"]

    expected, actual = ["Home", "Accounts"], ["Home", "Account"]
    mismatches = [(e, a) for e, a in zip(expected, actual) if e != a]
    assert mismatches == [("Accounts", "Account")]

    assert list(range(3)) == [0, 1, 2] and list(range(2, 10, 3)) == [2, 5, 8]  # stop is OUT

    totals = {"passed": 47, "failed": 3}
    assert [f"{k}={v}" for k, v in totals.items()] == ["passed=47", "failed=3"]  # dict loop


# ── 4. break, continue, and the loop-else ───────────────────────────────────────────────────
# HOOK  "Loop-else = 'no break' ": the else runs only if the loop finished WITHOUT break.
def find_first_failed(results: list[tuple[str, str]]) -> str:
    for name, status in results:
        if status == "skipped":
            continue  # skip to the next item
        if status == "failed":
            found = name
            break  # leave the loop now
    else:  # ← belongs to the FOR: runs only when no break happened
        return "all good"
    return found


def test_break_continue_else():
    assert find_first_failed([("a", "passed"), ("b", "skipped"), ("c", "failed")]) == "c"
    assert find_first_failed([("a", "passed")]) == "all good"


# ── 5. while LOOPS: repeat until a condition changes ────────────────────────────────────────
# HOOK  "while needs an EXIT": something inside must change the condition, or it never ends.
def test_while_with_a_limit():
    attempts, max_attempts, ready = 0, 5, False
    while not ready and attempts < max_attempts:  # ALWAYS cap it in test code
        attempts += 1
        ready = attempts == 3  # pretend the page becomes ready on try 3
    assert (ready, attempts) == (True, 3)


# ── 6. match / case (Python 3.10+) ──────────────────────────────────────────────────────────
# HOOK  "switch with X-ray vision": it matches values AND the SHAPE of data.
def describe(response: dict) -> str:
    match response:
        case {"responseCode": 200, "products": [first, *_]}:  # shape + capture variables
            return f"ok, first product {first}"
        case {"responseCode": 200}:
            return "ok, empty"
        case {"responseCode": 400 | 405 as code}:  # | = or; `as` captures the value
            return f"client error {code}"
        case _:  # _ = anything else (the default)
            return "unexpected"


@pytest.mark.parametrize(
    "response, expected",
    [
        ({"responseCode": 200, "products": ["Blue Top", "Hat"]}, "ok, first product Blue Top"),
        ({"responseCode": 200, "products": []}, "ok, empty"),
        ({"responseCode": 405}, "client error 405"),
        ({"oops": True}, "unexpected"),
    ],
)
def test_match(response, expected):
    assert describe(response) == expected


"""
SELF-CHECK
  1. When does a for-loop's else run?           → when the loop ends WITHOUT break
  2. "" or "default"?                           → "default"
  3. list(range(1, 4))?                         → [1, 2, 3]
  4. Index and value together?                  → enumerate(items)
  5. Why cap every while loop in tests?         → a never-true condition = a hung CI job
"""
