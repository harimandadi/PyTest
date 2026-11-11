"""
C05 · BASIC → INTERMEDIATE · LIST, TUPLE, SET, DICT
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "List = shopping list (ordered, editable, duplicates OK)
           Tuple = GPS coordinates (ordered, FIXED)
           Set = guest list (unique names, no order)
           Dict = phone book (look up a VALUE by its KEY)"

  [ ] list    ( ) tuple    { } set (with values)    {k: v} dict    {} alone = EMPTY DICT!

Run:  python -m pytest python/Python_Examples/Concepts/test_c05_data_structures.py -v
"""

import pytest


# ── 1. LIST ─────────────────────────────────────────────────────────────────────────────────
# HOOK  "append ADDS ONE, extend ADDS MANY, insert ADDS AT, pop TAKES, remove FINDS & TAKES"
def test_list_operations():
    steps = ["open", "login"]
    steps.append("transfer")  # ["open", "login", "transfer"]
    steps.extend(["verify", "logout"])  # adds each item
    steps.insert(0, "start")  # at index 0
    assert steps == ["start", "open", "login", "transfer", "verify", "logout"]
    assert steps.pop() == "logout"  # removes and RETURNS the last
    steps.remove("start")  # removes the first matching VALUE
    assert steps.index("login") == 1 and "verify" in steps and len(steps) == 4

    nums = [3, 1, 2]
    assert sorted(nums) == [1, 2, 3] and nums == [3, 1, 2]  # sorted() → NEW list
    assert nums.sort() is None and nums == [1, 2, 3]  # .sort() → IN PLACE, returns None!

    wrong = ["ab"]
    wrong.append([1, 2])  # append a list = ONE nested item
    assert wrong == ["ab", [1, 2]]


# ── 2. TUPLE ────────────────────────────────────────────────────────────────────────────────
# HOOK  "Tuple = a record that can't be edited": good for fixed data and dict KEYS.
def test_tuple():
    viewport = (1280, 720)
    width, height = viewport  # unpacking
    assert width == 1280
    single = ("chromium",)  # ONE-item tuple needs the comma
    assert type(single) is tuple and type(("chromium")) is str
    first, *rest = (1, 2, 3, 4)  # star unpacking: rest gets a LIST
    assert first == 1 and rest == [2, 3, 4]
    results = {("login", "chromium"): "passed"}  # tuples can be dict keys, lists can't
    assert results[("login", "chromium")] == "passed"
    with pytest.raises(TypeError):
        {["login"]: 1}  # type: ignore[dict-item]  list is unhashable


# ── 3. SET ──────────────────────────────────────────────────────────────────────────────────
# HOOK  "| all, & both, - only mine, ^ not shared" (union, intersection, difference, symmetric)
def test_set_operations():
    expected = {"Checking", "Savings", "Loan"}
    on_page = {"Savings", "Checking", "CD"}
    assert expected & on_page == {"Checking", "Savings"}  # in BOTH
    assert expected - on_page == {"Loan"}  # MISSING from the page
    assert on_page - expected == {"CD"}  # UNEXPECTED on the page
    assert expected | on_page == {"Checking", "Savings", "Loan", "CD"}
    assert expected ^ on_page == {"Loan", "CD"}
    assert set([1, 1, 2]) == {1, 2}  # duplicates vanish
    assert type({}) is dict and type(set()) is set  # {} is a DICT; empty set = set()
    # Membership: `x in a_set` is O(1); `x in a_list` scans everything, O(n).


# ── 4. DICT ─────────────────────────────────────────────────────────────────────────────────
# HOOK  "[] DEMANDS the key, .get() POLITELY ASKS": d["x"] raises KeyError, d.get("x") → None.
def test_dict_operations():
    user = {"name": "John", "role": "admin"}
    user["city"] = "Pune"  # add or overwrite
    assert user.get("phone") is None and user.get("phone", "n/a") == "n/a"
    with pytest.raises(KeyError):
        user["phone"]
    assert list(user.keys()) == ["name", "role", "city"]  # insertion order is kept (3.7+)
    assert user.pop("city") == "Pune" and "city" not in user
    user.update({"role": "user", "active": True})  # merge in place
    assert user == {"name": "John", "role": "user", "active": True}
    assert {**user, "role": "qa"}["role"] == "qa" and user["role"] == "user"  # copy + override

    counts: dict[str, int] = {}
    for status in ["passed", "failed", "passed"]:
        counts[status] = counts.get(status, 0) + 1  # the counting idiom
    assert counts == {"passed": 2, "failed": 1}

    groups: dict[str, list[str]] = {}
    for name, status in [("a", "passed"), ("b", "failed"), ("c", "passed")]:
        groups.setdefault(status, []).append(name)  # the grouping idiom
    assert groups == {"passed": ["a", "c"], "failed": ["b"]}


# ── 5. NESTED DATA (JSON is just dicts and lists) ───────────────────────────────────────────
# HOOK  "Read JSON from the outside in: one [ ] per level."
def test_nested_json_navigation():
    body = {"responseCode": 200, "products": [{"id": 1, "brand": {"name": "Polo"}}]}
    assert body["products"][0]["brand"]["name"] == "Polo"
    names = [p["brand"]["name"] for p in body["products"]]
    assert names == ["Polo"]


# ── 6. COPYING ──────────────────────────────────────────────────────────────────────────────
# HOOK  "Shallow copies the BOX, deep copies EVERYTHING inside."
def test_shallow_vs_deep():
    import copy

    template = {"user": {"name": "QA"}, "tags": ["smoke"]}
    shallow, deep = template.copy(), copy.deepcopy(template)
    shallow["tags"].append("api")  # inner list is SHARED with template
    deep["tags"].append("ui")
    assert template["tags"] == ["smoke", "api"]
    assert deep["tags"] == ["smoke", "ui"]


# ── 7. CHOOSING THE RIGHT ONE ───────────────────────────────────────────────────────────────
"""
  Need order + duplicates + changes?           → list       (test steps, results in order)
  Fixed record / dict key / function returns?  → tuple      (viewport, (test, browser) key)
  Uniqueness / fast "is it in there?"           → set        (seen ids, expected options)
  Look up by name?                              → dict       (config, JSON, counts)
  Counting? grouping?                           → collections.Counter / defaultdict (C06)

SELF-CHECK
  1. type({})?                                  → dict
  2. nums.sort() returns?                       → None (sorts in place)
  3. ("x") vs ("x",)?                           → str vs tuple
  4. d["k"] vs d.get("k") when k is missing?    → KeyError vs None
  5. Missing items on a page vs expected?       → expected - actual (set difference)
"""
