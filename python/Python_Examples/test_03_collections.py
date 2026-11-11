"""
03. DICTS, SETS AND NESTED DATA: what API test code does all day.

Run:  python -m pytest python/Python_Examples/test_03_collections.py -v
"""

from collections import defaultdict
from itertools import groupby

import pytest


# ── 1. Merge two dicts (right side wins) ────────────────────────────────────────────────────
def merge(defaults: dict, overrides: dict) -> dict:
    return defaults | overrides  # same as {**defaults, **overrides}


def test_merge():
    assert merge({"env": "qa", "workers": 2}, {"workers": 4}) == {"env": "qa", "workers": 4}


# ── 2. Deep merge (nested config) ───────────────────────────────────────────────────────────
def deep_merge(base: dict, extra: dict) -> dict:
    result = dict(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def test_deep_merge():
    base = {"browser": {"name": "chromium", "headless": True}, "retries": 0}
    assert deep_merge(base, {"browser": {"headless": False}}) == {"browser": {"name": "chromium", "headless": False}, "retries": 0}
    assert base["browser"]["headless"] is True  # original not mutated


# ── 3. Flatten a nested list (recursion) ────────────────────────────────────────────────────
def flatten(items: list) -> list:
    flat = []
    for item in items:
        flat.extend(flatten(item) if isinstance(item, list) else [item])
    return flat


def test_flatten():
    assert flatten([1, [2, [3, [4]], 5], []]) == [1, 2, 3, 4, 5]


# ── 4. Flatten a nested dict to dotted keys (great for comparing JSON) ──────────────────────
def flatten_dict(data: dict, prefix: str = "") -> dict:
    flat = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_dict(value, path))
        else:
            flat[path] = value
    return flat


def test_flatten_dict():
    assert flatten_dict({"user": {"name": "QA", "address": {"city": "Pune"}}, "id": 1}) == {
        "user.name": "QA",
        "user.address.city": "Pune",
        "id": 1,
    }


# ── 5. Group test results by status ─────────────────────────────────────────────────────────
RESULTS = [
    {"test": "login", "status": "passed", "ms": 1200},
    {"test": "transfer", "status": "failed", "ms": 3400},
    {"test": "logout", "status": "passed", "ms": 300},
    {"test": "bill_pay", "status": "skipped", "ms": 0},
]


def group_by_status(results: list[dict]) -> dict[str, list[str]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)  # no "if key not in" needed
    for r in results:
        groups[r["status"]].append(r["test"])
    return dict(groups)


def test_group_by_status():
    assert group_by_status(RESULTS) == {"passed": ["login", "logout"], "failed": ["transfer"], "skipped": ["bill_pay"]}


def test_groupby_needs_sorted_input():
    statuses = [r["status"] for r in RESULTS]
    unsorted_groups = [k for k, _ in groupby(statuses)]
    assert unsorted_groups == ["passed", "failed", "passed", "skipped"]  # ← "passed" twice!
    assert [k for k, _ in groupby(sorted(statuses))] == ["failed", "passed", "skipped"]


# ── 6. Sort by a key: slowest tests first, then by name ─────────────────────────────────────
def slowest(results: list[dict], top: int) -> list[str]:
    return [r["test"] for r in sorted(results, key=lambda r: (-r["ms"], r["test"]))[:top]]


def test_slowest():
    assert slowest(RESULTS, 2) == ["transfer", "login"]


# ── 7. Set operations: compare expected vs actual (e.g. dropdown options, column names) ─────
def compare_sets(expected: list[str], actual: list[str]) -> dict[str, set[str]]:
    exp, act = set(expected), set(actual)
    return {"missing": exp - act, "unexpected": act - exp, "common": exp & act}


def test_compare_sets():
    diff = compare_sets(["Checking", "Savings"], ["Savings", "Loan"])
    assert diff == {"missing": {"Checking"}, "unexpected": {"Loan"}, "common": {"Savings"}}


# ── 8. Invert a dict / find keys by value ───────────────────────────────────────────────────
def invert(data: dict[str, str]) -> dict[str, list[str]]:
    inverted: dict[str, list[str]] = {}
    for key, value in data.items():
        inverted.setdefault(value, []).append(key)
    return inverted


def test_invert():
    owners = {"login": "Asha", "transfer": "Ravi", "logout": "Asha"}
    assert invert(owners) == {"Asha": ["login", "logout"], "Ravi": ["transfer"]}


# ── 9. Safe nested lookup (no KeyError / TypeError chains) ──────────────────────────────────
def get_path(data, path: str, default=None):
    current = data
    for part in path.split("."):
        if isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current


@pytest.mark.parametrize(
    "path, expected",
    [("products.0.name", "Blue Top"), ("products.1.price", None), ("products.0.brand.name", None), ("responseCode", 200)],
)
def test_get_path(path, expected):
    body = {"responseCode": 200, "products": [{"name": "Blue Top", "price": "Rs. 500"}]}
    assert get_path(body, path) == expected


# ── 10. Chunk a list (batch API calls, split test data across workers) ──────────────────────
def chunks(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def test_chunks():
    assert chunks(list(range(7)), 3) == [[0, 1, 2], [3, 4, 5], [6]]


# ── 11. zip and enumerate: pair expected with actual, with positions ────────────────────────
def first_mismatch(expected: list, actual: list) -> tuple[int, object, object] | None:
    for i, (e, a) in enumerate(zip(expected, actual, strict=False)):
        if e != a:
            return i, e, a
    if len(expected) != len(actual):
        return min(len(expected), len(actual)), None, None
    return None


def test_first_mismatch():
    assert first_mismatch(["Home", "Accounts", "Transfer"], ["Home", "Account", "Transfer"]) == (1, "Accounts", "Account")
    assert first_mismatch([1, 2], [1, 2]) is None
    assert first_mismatch([1, 2, 3], [1, 2]) == (2, None, None)
