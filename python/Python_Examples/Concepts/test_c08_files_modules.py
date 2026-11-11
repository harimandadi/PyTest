"""
C08 · INTERMEDIATE · FILES, PATHS, JSON/CSV, MODULES, ENVIRONMENT
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "`with` = the door closes behind you." Files opened in a with-block are ALWAYS
          closed, even if the code inside fails.

Run:  python -m pytest python/Python_Examples/Concepts/test_c08_files_modules.py -v
(tmp_path is a pytest fixture: a fresh, empty folder for each test.)
"""

import csv
import json
import os
from pathlib import Path


# ── 1. pathlib: paths as OBJECTS ────────────────────────────────────────────────────────────
# HOOK  "Slash to join": Path("a") / "b" / "c.json" works on Windows AND Linux.
def test_pathlib(tmp_path: Path):
    report = tmp_path / "reports" / "run1" / "summary.json"
    assert report.name == "summary.json" and report.suffix == ".json" and report.stem == "summary"
    assert report.parent.name == "run1"
    report.parent.mkdir(parents=True, exist_ok=True)  # like mkdir -p
    report.write_text("{}", encoding="utf-8")
    assert report.exists() and report.is_file()
    assert [p.name for p in tmp_path.rglob("*.json")] == ["summary.json"]  # recursive search
    here = Path(__file__).resolve().parent  # "the folder this file is in": stable test data paths
    assert here.name == "Concepts"


# ── 2. READ AND WRITE TEXT ──────────────────────────────────────────────────────────────────
# HOOK  "Mode letters: r read, w WIPE-and-write, a append, x create-only, b binary"
def test_read_write_modes(tmp_path: Path):
    log = tmp_path / "run.log"
    with open(log, "w", encoding="utf-8") as f:  # ALWAYS pass encoding (Windows default isn't UTF-8)
        f.write("line 1\n")
    with open(log, "a", encoding="utf-8") as f:  # append keeps existing content
        f.write("line 2\n")
    with open(log, encoding="utf-8") as f:  # "r" is the default
        lines = [line.rstrip("\n") for line in f]  # iterate line by line: memory-friendly
    assert lines == ["line 1", "line 2"]
    assert f.closed  # the with-block closed it for us


# ── 3. JSON ─────────────────────────────────────────────────────────────────────────────────
# HOOK  "s = string": json.loads/dumps work on STRINGS, json.load/dump work on FILES.
def test_json(tmp_path: Path):
    payload = {"name": "QA", "active": True, "tags": ["smoke"], "manager": None}
    text = json.dumps(payload, indent=2)
    assert '"active": true' in text and '"manager": null' in text  # Python → JSON spelling
    assert json.loads(text) == payload  # round trip

    data_file = tmp_path / "user.json"
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    with open(data_file, encoding="utf-8") as f:
        assert json.load(f)["tags"] == ["smoke"]


# ── 4. CSV ──────────────────────────────────────────────────────────────────────────────────
# HOOK  "DictReader gives each row as a dict keyed by the header", and every value is a STRING.
def test_csv(tmp_path: Path):
    data = tmp_path / "logins.csv"
    with open(data, "w", newline="", encoding="utf-8") as f:  # newline="" avoids blank lines on Windows
        writer = csv.DictWriter(f, fieldnames=["user", "attempts"])
        writer.writeheader()
        writer.writerows([{"user": "john", "attempts": 3}, {"user": "jane", "attempts": 1}])
    with open(data, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0] == {"user": "john", "attempts": "3"}  # ← "3" is a STRING now
    assert sum(int(r["attempts"]) for r in rows) == 4


# ── 5. ENVIRONMENT VARIABLES ────────────────────────────────────────────────────────────────
# HOOK  "Secrets live in the environment, never in the code."
def test_env_vars(monkeypatch):
    monkeypatch.setenv("BASE_URL", "https://qa.example")  # pytest restores it after the test
    monkeypatch.delenv("API_TOKEN", raising=False)
    assert os.getenv("BASE_URL") == "https://qa.example"
    assert os.getenv("API_TOKEN", "missing") == "missing"  # default instead of None
    workers = int(os.getenv("WORKERS", "2"))  # env vars are STRINGS → convert
    assert workers == 2


# ── 6. MODULES AND IMPORTS ──────────────────────────────────────────────────────────────────
# HOOK  "A module is imported ONCE; later imports reuse the same object (cached in sys.modules)."
def test_import_caching():
    import sys

    import json as j1
    import json as j2

    assert j1 is j2 is sys.modules["json"]


"""
 IMPORT STYLES
   import json                     use as json.loads(...)     clear where it comes from
   from json import loads          use as loads(...)          shorter
   from pages.login import LoginPage                          from YOUR package
   import pandas as pd             alias
   from x import *                 ✗ avoid: you can't tell where names come from

 if __name__ == "__main__":
   HOOK "Am I the main show?"  Code under it runs when you execute the file directly
   (python tools/report.py) but NOT when another file imports it. Use it for small CLIs.

 PACKAGES
   a folder with __init__.py is a package: `from api.services import AuthApi`.
   pytest note: test folders don't need __init__.py, but then test file NAMES must be unique.
"""


def test_main_guard():
    assert __name__ != "__main__"  # pytest IMPORTED this file, so the guard would be skipped


"""
SELF-CHECK
  1. "w" on an existing file?                     → wipes it first
  2. json.loads vs json.load?                     → string vs file
  3. Why encoding="utf-8" everywhere?             → Windows default encoding isn't UTF-8
  4. CSV values come back as?                     → strings, always
  5. What does if __name__ == "__main__" do?      → runs only when the file is executed directly
"""
