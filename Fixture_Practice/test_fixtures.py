# Fixture practice: Level 1 (simple) → Level 8 (conftest). Run with:  pytest -v -s
import itertools

import pytest


# ---------------------------------------------------------------- Level 1: a fixture that returns data
@pytest.fixture
def user():
    return {"name": "Hari", "role": "SDET", "active": True}


def test_user_role(user):                      # the fixture is injected by its NAME
    assert user["role"] == "SDET"


def test_user_is_active(user):                 # each test gets a FRESH copy (function scope)
    user["active"] = False                     # changing it here doesn't affect other tests
    assert user["active"] is False


# ---------------------------------------------------------------- Level 2: setup + teardown with yield
@pytest.fixture
def db_connection():
    print("  [setup] open DB connection")
    connection = {"open": True, "rows": []}
    yield connection                           # ← the test runs here
    connection["open"] = False                 # ← teardown runs after the test (even if it fails)
    print("  [teardown] close DB connection")


def test_insert_row(db_connection):
    db_connection["rows"].append({"id": 1})
    assert db_connection["open"] is True
    assert len(db_connection["rows"]) == 1


# ---------------------------------------------------------------- Level 3: scopes (how often a fixture runs)
CALLS = {"function": 0, "module": 0}


@pytest.fixture                                # scope="function" (default): runs for EVERY test
def per_test_counter():
    CALLS["function"] += 1
    return CALLS["function"]


@pytest.fixture(scope="module")                # runs ONCE for this whole file
def per_module_counter():
    CALLS["module"] += 1
    return CALLS["module"]


def test_scope_first(per_test_counter, per_module_counter):
    assert per_test_counter == 1 and per_module_counter == 1


def test_scope_second(per_test_counter, per_module_counter):
    assert per_test_counter == 2               # created again → 2
    assert per_module_counter == 1             # reused → still 1


# ---------------------------------------------------------------- Level 4: a fixture that uses other fixtures
@pytest.fixture
def api_client(base_url):                      # base_url comes from conftest.py
    return {"base_url": base_url, "headers": {"Authorization": "Bearer test-token"}}


@pytest.fixture
def logged_in_user(api_client, user):          # fixtures can depend on fixtures
    return {**user, "token": api_client["headers"]["Authorization"]}


def test_logged_in_user(logged_in_user, api_client):
    assert logged_in_user["token"].startswith("Bearer")
    assert api_client["base_url"] == "https://qa.example.com"


# ---------------------------------------------------------------- Level 5: built-in fixtures
def test_tmp_path_writes_a_file(tmp_path):     # tmp_path = a fresh temporary folder per test
    report = tmp_path / "report.txt"
    report.write_text("PASS: 10\nFAIL: 0")
    assert report.read_text().splitlines()[0] == "PASS: 10"


def test_monkeypatch_env(monkeypatch):         # monkeypatch = change env vars safely (auto-restored)
    import os
    monkeypatch.setenv("TEST_ENV", "staging")
    assert os.environ["TEST_ENV"] == "staging"


# ---------------------------------------------------------------- Level 6: factory fixture (unique test data)
@pytest.fixture
def make_user():
    counter = itertools.count(1)
    created = []

    def _make(role="viewer"):                  # the fixture RETURNS A FUNCTION
        new_user = {"id": next(counter), "email": f"user{len(created) + 1}@qa.com", "role": role}
        created.append(new_user)
        return new_user

    yield _make
    print(f"  [teardown] delete {len(created)} test users")   # clean up everything that was created


def test_factory_creates_unique_users(make_user):
    admin = make_user("admin")
    viewer = make_user()
    assert admin["id"] != viewer["id"]
    assert admin["role"] == "admin" and viewer["role"] == "viewer"


# ---------------------------------------------------------------- Level 7 (autouse) is in conftest.py: log_test_name

# ---------------------------------------------------------------- Level 8: parametrized fixture (run a test per value)
@pytest.fixture(params=["chromium", "firefox", "webkit"])
def browser_name(request):                     # request.param = the current value
    return request.param


def test_runs_on_every_browser(browser_name):  # this ONE test runs 3 times
    assert browser_name in {"chromium", "firefox", "webkit"}