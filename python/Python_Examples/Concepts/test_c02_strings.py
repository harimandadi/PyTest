"""
C02 · BASIC · STRINGS AND SLICING
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "[start : stop : step]: start is IN, stop is OUT."
          Like a train ticket valid from station 1 UP TO (not including) station 4.

Run:  python -m pytest python/Python_Examples/Concepts/test_c02_strings.py -v
"""

import pytest

TEXT = "ParaBank"
#        P a r a B a n k
# index  0 1 2 3 4 5 6 7
# neg   -8-7-6-5-4-3-2-1


# ── 1. INDEXING AND SLICING ─────────────────────────────────────────────────────────────────
# HOOK  "Negative counts from the END: -1 is the last."
def test_indexing_and_slicing():
    assert TEXT[0] == "P" and TEXT[-1] == "k"
    assert TEXT[0:4] == "Para"  # 0,1,2,3 → stop (4) is OUT
    assert TEXT[4:] == "Bank"  # missing stop = to the end
    assert TEXT[:4] == "Para"  # missing start = from the beginning
    assert TEXT[-4:] == "Bank"  # the last 4
    assert TEXT[::2] == "PrBn"  # every 2nd character
    assert TEXT[::-1] == "knaBaraP"  # step -1 = backwards = reverse
    assert TEXT[100:] == ""  # slicing NEVER raises IndexError…
    with pytest.raises(IndexError):
        TEXT[100]  # …but indexing does


# ── 2. THE METHODS YOU USE EVERY DAY ────────────────────────────────────────────────────────
# HOOK  "Strings never change: every method RETURNS a new string."
def test_everyday_methods():
    raw = "  Welcome John Smith  "
    assert raw.strip() == "Welcome John Smith"  # trim both ends (UI text!)
    assert raw.strip().lower() == "welcome john smith"
    assert raw.strip().upper().startswith("WELCOME")
    assert raw.strip().replace("John", "Jane") == "Welcome Jane Smith"
    assert raw.strip().split() == ["Welcome", "John", "Smith"]  # split on ANY whitespace
    assert "a,b,,c".split(",") == ["a", "b", "", "c"]  # split on a char keeps empties
    assert "-".join(["2026", "11", "11"]) == "2026-11-11"  # join: separator.join(list)
    assert raw.strip() != raw  # the original is unchanged
    assert "john" in raw.lower()  # substring check
    assert raw.find("Zed") == -1  # find → -1 if missing; index() would raise ValueError
    assert "Total: 42".split(": ")[1] == "42"  # pull a value out of a label
    assert "TC-007".zfill(8) == "00TC-007" and "7".zfill(3) == "007"  # pad with zeros
    assert "123".isdigit() and not "12.3".isdigit()  # validation helpers


# ── 3. COMPARING UI TEXT SAFELY ─────────────────────────────────────────────────────────────
# HOOK  "Normalise BOTH sides, then compare."
def normalise(text: str) -> str:
    return " ".join(text.split()).casefold()  # collapse whitespace + strongest lowercase


def test_normalised_compare():
    from_ui = "  Account   Opened\nSuccessfully "
    assert normalise(from_ui) == normalise("account opened successfully")
    assert "STRASSE".casefold() == "straße".casefold()  # casefold > lower for international text


# ── 4. MULTI-LINE AND RAW STRINGS ───────────────────────────────────────────────────────────
# HOOK  "r for raw: backslashes stay backslashes" (regex and Windows paths).
def test_raw_and_multiline():
    assert len("\n") == 1 and len(r"\n") == 2  # escape vs two literal characters
    path = r"C:\new\tests"  # without r: \n = newline, \t = tab → broken path
    assert "\\" in path
    body = """{
  "user": "qa"
}"""
    assert body.count("\n") == 2


# ── 5. BUILDING STRINGS EFFICIENTLY ─────────────────────────────────────────────────────────
# HOOK  "Collect in a list, join ONCE."  (s += in a loop copies the string every time)
def test_join_beats_concatenation():
    rows = [f"row {i}" for i in range(3)]
    report = "\n".join(rows)
    assert report == "row 0\nrow 1\nrow 2"


# ── 6. COUNTING AND CHECKING ────────────────────────────────────────────────────────────────
def test_count_and_check():
    msg = "Error: login failed. Error code 500."
    assert msg.count("Error") == 2
    assert msg.startswith(("Error", "Warning"))  # startswith accepts a TUPLE of options
    assert msg.endswith(".")
    assert msg.partition(": ") == ("Error", ": ", "login failed. Error code 500.")


"""
SELF-CHECK
  1. "ParaBank"[2:5]?                        → "raB"   (2,3,4; 5 is OUT)
  2. Reverse a string in one expression?     → s[::-1]
  3. s.upper() didn't change s. Why?         → strings are immutable; methods return new ones
  4. find vs index when missing?             → -1 vs ValueError
  5. Why r"..." for regex?                   → keeps backslashes literal
"""
