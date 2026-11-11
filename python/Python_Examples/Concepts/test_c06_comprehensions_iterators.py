"""
C06 · INTERMEDIATE · COMPREHENSIONS, ITERATORS, GENERATORS, collections, itertools
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "[ WHAT  for ITEM in WHERE  if FILTER ]": read a comprehension as a sentence:
          "give me WHAT, for each ITEM in WHERE, but only IF FILTER".

Run:  python -m pytest python/Python_Examples/Concepts/test_c06_comprehensions_iterators.py -v
"""

from collections import Counter, defaultdict, deque, namedtuple
from itertools import chain, count, cycle, groupby, islice, product

import pytest

RESULTS = [("login", "passed", 1.2), ("transfer", "failed", 3.4), ("logout", "passed", 0.3), ("billpay", "skipped", 0.0)]


# ── 1. LIST / DICT / SET COMPREHENSIONS ─────────────────────────────────────────────────────
# HOOK  The bracket decides the result: [ ] list, { k: v } dict, { x } set, ( ) generator.
def test_comprehensions():
    passed = [name for name, status, _ in RESULTS if status == "passed"]
    assert passed == ["login", "logout"]

    durations = {name: secs for name, _, secs in RESULTS}  # dict comprehension
    assert durations["transfer"] == 3.4

    statuses = {status for _, status, _ in RESULTS}  # set comprehension: unique
    assert statuses == {"passed", "failed", "skipped"}

    labels = ["SLOW" if secs > 1 else "fast" for _, _, secs in RESULTS]  # if-ELSE goes FIRST
    assert labels == ["SLOW", "SLOW", "fast", "fast"]

    grid = [(b, v) for b in ["chromium", "firefox"] for v in ["desktop", "mobile"]]  # nested: left loop is OUTER
    assert len(grid) == 4 and grid[1] == ("chromium", "mobile")


# ── 2. ITERABLE vs ITERATOR ─────────────────────────────────────────────────────────────────
# HOOK  "Iterable = the BOOK, iterator = the BOOKMARK."  A list can be read many times;
#        an iterator remembers its position and is USED UP after one pass.
def test_iterator_protocol():
    browsers = ["chromium", "firefox"]  # iterable
    it = iter(browsers)  # iterator (bookmark)
    assert next(it) == "chromium"
    assert next(it) == "firefox"
    with pytest.raises(StopIteration):  # this is how a for-loop knows when to stop
        next(it)

    gen = (b.upper() for b in browsers)
    assert list(gen) == ["CHROMIUM", "FIREFOX"]
    assert list(gen) == []  # ← EXHAUSTED: a generator can be consumed only once!


# ── 3. GENERATORS (yield) ───────────────────────────────────────────────────────────────────
# HOOK  "return gives ONE answer and leaves; yield gives one, PAUSES, and continues on demand."
# WHY (QA)  Stream a 2 GB log or 1M DB rows without loading them all into memory.
def read_pages(total_items: int, page_size: int):
    """Simulates a paginated API: yields one page at a time, only when asked."""
    for start in range(0, total_items, page_size):
        yield list(range(start, min(start + page_size, total_items)))


def test_generator_pagination():
    pages = read_pages(total_items=7, page_size=3)
    assert next(pages) == [0, 1, 2]  # only the first page was "fetched"
    assert [item for page in pages for item in page] == [3, 4, 5, 6]  # flatten the rest


def test_generator_expression_saves_memory():
    import sys

    as_list = [n * n for n in range(100_000)]
    as_gen = (n * n for n in range(100_000))
    assert sys.getsizeof(as_gen) < 500 < sys.getsizeof(as_list)  # tiny vs ~800 KB
    assert sum(n * n for n in range(4)) == 14  # no extra brackets needed inside a call


def test_yield_from():
    def nested():
        yield "setup"
        yield from ["step1", "step2"]  # delegate to another iterable
        yield "teardown"

    assert list(nested()) == ["setup", "step1", "step2", "teardown"]


# ── 4. BUILT-INS THAT TAKE ITERABLES ────────────────────────────────────────────────────────
# HOOK  "any = at least one, all = every one" (and all([]) is True: nothing failed!)
def test_any_all_sum_min_max_sorted():
    statuses = [s for _, s, _ in RESULTS]
    assert any(s == "failed" for s in statuses)
    assert not all(s == "passed" for s in statuses)
    assert all([]) is True and any([]) is False  # empty-collection edge case
    assert round(sum(secs for *_, secs in RESULTS), 1) == 4.9
    assert min(RESULTS, key=lambda r: r[2])[0] == "billpay"
    assert sorted(RESULTS, key=lambda r: (r[1], -r[2]))[0][0] == "transfer"  # status, then slowest


# ── 5. collections: Counter, defaultdict, deque, namedtuple ─────────────────────────────────
# HOOK  "Counter COUNTS, defaultdict never says KeyError, deque is a two-door queue,
#        namedtuple is a tuple with labels."
def test_collections():
    c = Counter(s for _, s, _ in RESULTS)
    assert c["passed"] == 2 and c["unknown"] == 0  # missing key → 0, no KeyError
    assert c.most_common(1) == [("passed", 2)]

    by_status = defaultdict(list)  # missing key → creates an empty list automatically
    for name, status, _ in RESULTS:
        by_status[status].append(name)
    assert by_status["failed"] == ["transfer"]

    recent = deque(maxlen=3)  # keeps only the LAST 3: great for "last N log lines"
    for line in ["l1", "l2", "l3", "l4"]:
        recent.append(line)
    assert list(recent) == ["l2", "l3", "l4"]

    Result = namedtuple("Result", "name status secs")
    r = Result(*RESULTS[0])
    assert r.name == "login" and r[1] == "passed"  # by name AND by position


# ── 6. itertools: the lazy toolbox ──────────────────────────────────────────────────────────
# HOOK  "chain JOINS, product COMBINES, groupby needs SORTED, islice CUTS, cycle REPEATS"
def test_itertools():
    assert list(chain(["a"], ["b", "c"])) == ["a", "b", "c"]
    combos = list(product(["chromium", "firefox"], ["en", "de"]))  # every browser × locale
    assert len(combos) == 4 and ("firefox", "de") in combos
    assert list(islice(count(start=100), 3)) == [100, 101, 102]  # endless counter, cut to 3
    workers = cycle(["gw0", "gw1"])  # round-robin assignment
    assert [next(workers) for _ in range(3)] == ["gw0", "gw1", "gw0"]
    data = sorted(["passed", "failed", "passed"])  # groupby ONLY groups NEIGHBOURS → sort first
    assert {k: len(list(g)) for k, g in groupby(data)} == {"failed": 1, "passed": 2}


# ── 7. ZIP AND ENUMERATE, REVISITED ─────────────────────────────────────────────────────────
# HOOK  "zip stops at the SHORTEST": use strict=True when lengths MUST match.
def test_zip_strict():
    assert list(zip([1, 2, 3], ["a", "b"])) == [(1, "a"), (2, "b")]  # 3 silently dropped!
    with pytest.raises(ValueError):
        list(zip([1, 2, 3], ["a", "b"], strict=True))  # 3.10+: catch length mismatches
    names, statuses, _ = zip(*RESULTS)  # zip(*rows) = TRANSPOSE (rows → columns)
    assert names == ("login", "transfer", "logout", "billpay")


"""
SELF-CHECK
  1. [x for x in data if x > 0] vs [x if x > 0 else 0 for x in data]: where does `if` go?
     → filter-if at the END; if-else expression at the FRONT
  2. Why is a generator empty the second time?       → iterators are used up after one pass
  3. all([])?                                        → True
  4. groupby gave duplicate groups. Why?             → input wasn't sorted by the key
  5. Count words in one line?                        → Counter(words)
"""
