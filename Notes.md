# 🧪 pytest Cheat Sheet

> Run tests · Select tests · Debug · Reports · Assertions · Fixtures · Parametrize · Markers

---

## 1. Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (macOS/Linux: source .venv/bin/activate)
pip install pytest
pip install pytest-xdist pytest-html pytest-cov pytest-rerunfailures   # optional plugins
pip freeze > requirements.txt
pytest --version
```

**File and test naming (auto-discovery)**
- Files: `test_*.py` or `*_test.py`
- Functions: `test_*`
- Classes: `Test*` (no `__init__` method)

---

## 2. Run tests

```bash
py -m pytest -v
pytest                                   # run all tests
pytest -v                                # verbose (each test name + result)
pytest -q                                # quiet
pytest tests/test_login.py               # one file
pytest tests/test_login.py::test_valid   # one test
pytest tests/test_api.py::TestUsers::test_get_user   # test inside a class
pytest tests/api/                        # one folder
```

## 3. Select tests

```bash
pytest -k "login"                        # name contains "login"
pytest -k "login and not slow"           # and / or / not
pytest -m smoke                          # marker
pytest -m "smoke or regression"
pytest --collect-only -q                 # LIST tests without running them
```

## 4. Re-run and stop

```bash
pytest -x                                # stop at first failure
pytest --maxfail=3                       # stop after 3 failures
pytest --lf                              # run only Last Failed
pytest --ff                              # Failed First, then the rest
pytest --sw                              # stepwise: continue from the last failure
```

## 5. Debug

```bash
pytest -s                                # show print() output
pytest -vv                               # full diff for long lists/dicts/strings
pytest --tb=short                        # short traceback (long | short | line | no)
pytest -l                                # show local variables in tracebacks
pytest --pdb                             # open debugger at the failure
pytest -rA                               # summary of all results
pytest -rfE                              # summary of failures + errors only
pytest --setup-show                      # show fixture setup/teardown order
```

## 6. Performance and reports

```bash
pytest --durations=5                     # 5 slowest tests
pytest -n 4                              # 4 parallel workers        (pytest-xdist)
pytest -n auto                           # one worker per CPU core   (pytest-xdist)
pytest --html=report.html --self-contained-html   # HTML report     (pytest-html)
pytest --junitxml=results.xml            # JUnit XML for CI (built in)
pytest --cov=src --cov-report=html       # coverage                  (pytest-cov)
pytest --reruns 2 --reruns-delay 1       # retry flaky tests         (pytest-rerunfailures)
```

## 7. Inspect

```bash
pytest --fixtures                        # list available fixtures
pytest --markers                         # list registered markers
pytest --version
```

---

## 8. Assertions (compare and verify)

```python
import pytest

def test_compare():
    status, body = 200, {"id": 7, "name": "Hari", "roles": ["admin"]}

    assert status == 200                       # equal
    assert status != 404                       # not equal
    assert body["name"] == "Hari"              # dict value
    assert "admin" in body["roles"]            # in list
    assert "Har" in body["name"]               # substring
    assert body.get("manager") is None         # None check (use "is")
    assert isinstance(body["id"], int)         # type
    assert len(body["roles"]) == 1             # length
    assert body == {"id": 7, "name": "Hari", "roles": ["admin"]}   # whole dict
    assert {"a", "b"} <= {"a", "b", "c"}       # subset
    assert 0.1 + 0.2 == pytest.approx(0.3)     # floats
    assert status in (200, 201), f"Unexpected status {status}"     # custom message


def test_exceptions():
    with pytest.raises(ZeroDivisionError):
        1 / 0
    with pytest.raises(ValueError, match="invalid"):
        raise ValueError("invalid user id")
```

| TestNG / JUnit | pytest |
|---|---|
| `assertEquals(a, b)` | `assert a == b` |
| `assertNotEquals(a, b)` | `assert a != b` |
| `assertTrue(x)` / `assertFalse(x)` | `assert x` / `assert not x` |
| `assertNull(x)` | `assert x is None` |
| `list.contains(v)` | `assert v in my_list` |
| `assertEquals(0.3, x, 0.0001)` | `assert x == pytest.approx(0.3)` |
| `assertThrows(Ex.class, ...)` | `with pytest.raises(Ex):` |
| `SoftAssert` | plugin `pytest-check` |

---

## 9. Fixtures (setup / teardown)

```python
import pytest

@pytest.fixture
def user():
    return {"name": "Hari", "role": "SDET"}

@pytest.fixture(scope="session")          # function (default) | class | module | session
def api_client():
    client = {"base_url": "https://example.com"}   # setup
    yield client                                   # test runs here
    print("teardown: close client")                # teardown

def test_user(user, api_client):          # fixtures injected by NAME
    assert user["role"] == "SDET"
    assert api_client["base_url"].startswith("https")
```

**Built-in fixtures:** `tmp_path` (temp folder), `monkeypatch` (env vars / patch), `capsys` (capture prints), `request` (test info)

**`conftest.py`** = fixtures shared by every test in that folder (no import needed).

---

## 10. Parametrize (data-driven tests)

```python
import pytest

@pytest.mark.parametrize("value, expected", [
    ("madam", True),
    ("hello", False),
], ids=["palindrome", "not-palindrome"])
def test_palindrome(value, expected):
    assert (value == value[::-1]) == expected

@pytest.mark.parametrize("user, password, ok", [
    ("admin", "secret", True),
    ("admin", "wrong", False),
])
def test_login(user, password, ok):
    assert (password == "secret") == ok
```

---

## 11. Markers (tags, skip, xfail)

```python
import sys
import pytest

@pytest.mark.smoke
def test_homepage(): ...

@pytest.mark.skip(reason="feature not ready")
def test_new_feature(): ...

@pytest.mark.skipif(sys.platform == "win32", reason="Linux only")
def test_linux_only(): ...

@pytest.mark.xfail(reason="known bug JIRA-123")
def test_known_bug():
    assert 1 == 2
```

---

## 12. pytest.ini (save default options)

```ini
[pytest]
addopts = -v --tb=short -rfE
testpaths = tests
markers =
    smoke: quick critical tests
    regression: full suite
```

---

## 13. Project structure

```
project/
├── pytest.ini
├── requirements.txt
├── conftest.py            # shared fixtures
├── pages/                 # page objects
├── utils/                 # helpers, API clients
└── tests/
    ├── conftest.py        # folder-level fixtures
    ├── test_login.py
    └── api/
        └── test_users.py
```

---

## 14. Top 8 daily commands

```bash
pytest -v                  # run all
pytest -k "name"           # by name
pytest -m smoke            # by marker
pytest -x                  # stop at first failure
pytest --lf                # re-run last failures
pytest -s -vv              # debug: prints + full diff
pytest --collect-only -q   # verify what will run
pytest -n 4                # parallel (pytest-xdist)
```

## 🧠 Memory hooks

- `-k` = **keyword** · `-m` = **marker** · `-x` = **exit** on first failure · `-s` = **show** prints
- `--lf` = **Last Failed** · `--ff` = **Failed First**
- Floats → `approx` · Errors → `raises` · Everything else → `assert`
- Fixture = **@BeforeMethod/@AfterMethod** · parametrize = **@DataProvider** · marker = **TestNG group**
- `yield` in a fixture = "**setup above, test runs here, teardown below**"