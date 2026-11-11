"""
05. QA LEAD UTILITIES: the programs that show you think like a framework owner.

Run:  python -m pytest python/Python_Examples/test_05_qa_utilities.py -v
Each one is a real task a QA lead writes: parse logs, diff JSON, mask secrets, read test data,
summarise JUnit results, poll for a condition, validate UI sorting, generate unique data.
"""

import csv
import json
import re
import time
import uuid
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pytest


# ── 1. Parse a log file: count levels and collect error messages ────────────────────────────
LOG = """\
2026-11-10 10:00:01 INFO  Starting run on env=qa
2026-11-10 10:00:05 ERROR Login failed for user=john status=500
2026-11-10 10:00:07 WARN  Retrying request /transfer
2026-11-10 10:00:09 ERROR Timeout after 30000ms on /billpay
2026-11-10 10:00:10 INFO  Run finished
"""
LINE = re.compile(r"^(\S+ \S+) (INFO|WARN|ERROR)\s+(.*)$")


def parse_log(text: str) -> tuple[Counter, list[str]]:
    levels, errors = Counter(), []
    for line in text.splitlines():
        match = LINE.match(line)
        if not match:
            continue  # tolerate junk lines instead of crashing
        _, level, message = match.groups()
        levels[level] += 1
        if level == "ERROR":
            errors.append(message)
    return levels, errors


def test_parse_log(tmp_path: Path):
    log_file = tmp_path / "run.log"
    log_file.write_text(LOG + "garbage line\n")
    levels, errors = parse_log(log_file.read_text())
    assert levels == {"INFO": 2, "ERROR": 2, "WARN": 1}
    assert errors[1] == "Timeout after 30000ms on /billpay"


# ── 2. Diff two JSON responses (expected vs actual), reporting every path ───────────────────
def json_diff(expected, actual, path: str = "$") -> list[str]:
    diffs: list[str] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in expected.keys() | actual.keys():
            if key not in actual:
                diffs.append(f"{path}.{key}: missing")
            elif key not in expected:
                diffs.append(f"{path}.{key}: unexpected")
            else:
                diffs += json_diff(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            diffs.append(f"{path}: length {len(expected)} != {len(actual)}")
        for i, (e, a) in enumerate(zip(expected, actual)):
            diffs += json_diff(e, a, f"{path}[{i}]")
    elif expected != actual:
        diffs.append(f"{path}: {expected!r} != {actual!r}")
    return sorted(diffs)


def test_json_diff():
    expected = {"id": 1, "name": "Blue Top", "tags": ["women", "tops"], "price": "Rs. 500"}
    actual = {"id": 1, "name": "Blue top", "tags": ["women"], "stock": 3}
    assert json_diff(expected, actual) == [
        "$.name: 'Blue Top' != 'Blue top'",
        "$.price: missing",
        "$.stock: unexpected",
        "$.tags: length 2 != 1",
    ]
    assert json_diff(expected, json.loads(json.dumps(expected))) == []


# ── 3. Mask sensitive data before it reaches logs and reports ───────────────────────────────
SECRETS = [
    (re.compile(r'("password"\s*:\s*")[^"]*(")'), r"\1****\2"),
    (re.compile(r"(Bearer\s+)[\w.-]+"), r"\1****"),
    (re.compile(r"\b(\d{4})\d{8}(\d{4})\b"), r"\1********\2"),  # 16-digit card number
]


def mask(text: str) -> str:
    for pattern, replacement in SECRETS:
        text = pattern.sub(replacement, text)
    return text


def test_mask():
    raw = 'Authorization: Bearer eyJhbGc.abc-123 body={"user": "john", "password": "demo123"} card=4111111111111111'
    assert mask(raw) == 'Authorization: Bearer **** body={"user": "john", "password": "****"} card=4111********1111'


# ── 4. Validate an email (and test the validator with boundary cases) ──────────────────────
EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


@pytest.mark.parametrize(
    "email, valid",
    [
        ("qa.lead@example.com", True),
        ("a+tag@sub.example.co.in", True),
        ("no-at-sign.com", False),
        ("two@@example.com", False),
        ("user@nodot", False),
        ("user@example.c", False),
        ("", False),
    ],
)
def test_email_validation(email, valid):
    assert bool(EMAIL.fullmatch(email)) is valid


# ── 5. Read test data from CSV and JSON (data-driven tests) ─────────────────────────────────
def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:  # newline="" is the csv module's rule
        return list(csv.DictReader(f))


def test_load_csv_and_json(tmp_path: Path):
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("username,password,expected\njohn,demo,success\nbad,bad,error\n", encoding="utf-8")
    rows = load_csv(csv_file)
    assert rows[0] == {"username": "john", "password": "demo", "expected": "success"}

    json_file = tmp_path / "users.json"
    json_file.write_text(json.dumps(rows), encoding="utf-8")
    assert json.loads(json_file.read_text(encoding="utf-8")) == rows


# ── 6. Summarise a JUnit XML report (what CI dashboards do) ─────────────────────────────────
JUNIT = """<testsuites>
  <testsuite name="ui" tests="4">
    <testcase classname="login" name="valid" time="1.2"/>
    <testcase classname="login" name="invalid" time="0.8"><failure message="expected error"/></testcase>
    <testcase classname="transfer" name="funds" time="3.1"/>
    <testcase classname="billpay" name="pay" time="0"><skipped/></testcase>
  </testsuite>
</testsuites>"""


def junit_summary(xml_text: str) -> dict:
    cases = ET.fromstring(xml_text).iter("testcase")
    summary = Counter()
    failed: list[str] = []
    for case in cases:
        if case.find("failure") is not None or case.find("error") is not None:
            summary["failed"] += 1
            failed.append(f"{case.get('classname')}.{case.get('name')}")
        elif case.find("skipped") is not None:
            summary["skipped"] += 1
        else:
            summary["passed"] += 1
    executed = summary["passed"] + summary["failed"]
    return {**summary, "pass_rate": round(100 * summary["passed"] / executed, 1) if executed else 0.0, "failed_tests": failed}


def test_junit_summary():
    assert junit_summary(JUNIT) == {"passed": 2, "failed": 1, "skipped": 1, "pass_rate": 66.7, "failed_tests": ["login.invalid"]}


# ── 7. Poll until a condition is true (instead of time.sleep) ───────────────────────────────
def wait_until(condition, timeout_s: float = 5.0, interval_s: float = 0.05, message: str = "condition"):
    deadline = time.monotonic() + timeout_s  # monotonic: immune to clock changes
    while True:
        result = condition()
        if result:
            return result
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{message} not met within {timeout_s}s")
        time.sleep(interval_s)


def test_wait_until():
    calls = {"n": 0}

    def job_finished():
        calls["n"] += 1
        return "DONE" if calls["n"] >= 3 else None

    assert wait_until(job_finished, timeout_s=2) == "DONE"
    with pytest.raises(TimeoutError, match="report generated"):
        wait_until(lambda: False, timeout_s=0.1, message="report generated")


# ── 8. Verify UI sorting (a table sorted by a column) ───────────────────────────────────────
def is_sorted(values: list, key=None, reverse: bool = False) -> bool:
    return values == sorted(values, key=key, reverse=reverse)


def parse_amount(text: str) -> float:
    return float(text.replace("$", "").replace(",", ""))


def test_ui_sort_validation():
    balances_on_page = ["$1,200.00", "$950.50", "$15.00"]  # what get_text() returns
    assert not is_sorted(balances_on_page, reverse=True)  # string sort is WRONG for money…
    assert is_sorted(balances_on_page, key=parse_amount, reverse=True)  # …sort by the number


# ── 9. Unique test data (parallel-safe) ─────────────────────────────────────────────────────
def unique_email(prefix: str = "qa") -> str:
    return f"{prefix}.{uuid.uuid4().hex[:10]}@example.com"


def test_unique_email():
    emails = {unique_email() for _ in range(1000)}
    assert len(emails) == 1000
    assert all(e.endswith("@example.com") for e in emails)


# ── 10. Business-day date math (due dates, scheduled payments) ──────────────────────────────
def add_business_days(start: date, days: int) -> date:
    current = start
    while days > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon=0 … Fri=4
            days -= 1
    return current


def test_add_business_days():
    friday = date(2026, 11, 13)
    assert add_business_days(friday, 1) == date(2026, 11, 16)  # skips the weekend → Monday
    assert add_business_days(friday, 5) == date(2026, 11, 20)


# ── 11. Find flaky tests from several runs ──────────────────────────────────────────────────
def flaky_tests(runs: list[dict[str, str]]) -> list[str]:
    """A test is flaky if, with the same code, it both passed and failed across runs."""
    outcomes: dict[str, set[str]] = {}
    for run in runs:
        for test, status in run.items():
            outcomes.setdefault(test, set()).add(status)
    return sorted(t for t, s in outcomes.items() if {"passed", "failed"} <= s)


def test_flaky_tests():
    runs = [
        {"login": "passed", "transfer": "failed", "logout": "passed"},
        {"login": "passed", "transfer": "passed", "logout": "passed"},
        {"login": "failed", "transfer": "passed", "logout": "passed"},
    ]
    assert flaky_tests(runs) == ["login", "transfer"]


# ── 12. Parse a URL and its query string ────────────────────────────────────────────────────
def test_parse_url():
    from urllib.parse import parse_qs, urlparse

    url = urlparse("https://parabank.parasoft.com/parabank/activity.htm?id=13344&month=All&type=Debit")
    query = {k: v[0] for k, v in parse_qs(url.query).items()}
    assert url.netloc == "parabank.parasoft.com" and url.path.endswith("activity.htm")
    assert query == {"id": "13344", "month": "All", "type": "Debit"}
