"""
LAYER 2: WIRING. conftest.py is pytest's fixtures/apiTest.ts + fixtures/baseTest.ts.

  • pytest finds conftest.py automatically (never import it). Fixtures here are visible to every
    test in this folder and below; a conftest.py in a sub-folder can add or OVERRIDE fixtures.
  • Hooks here (pytest_addoption, pytest_collection_modifyitems, ...) customise pytest itself.

Guide: test_python_pytest_essentials.py, section 4 (fixtures) and section 7 (hooks).
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator

import pytest

from framework import (
    AccountApi,
    ApiClient,
    AuthApi,
    EnvironmentConfig,
    FakeAutomationExerciseServer,
    NewUser,
    ProductsApi,
    build_user,
    expect_api_code,
    get_environment,
)

# ── HOOKS ──────────────────────────────────────────────────────────────────────────────────────


def pytest_addoption(parser: pytest.Parser) -> None:
    """Adds `pytest --env prod`. TS equivalent: TEST_ENV=prod npx playwright test."""
    parser.addoption(
        "--env",
        default=os.getenv("TEST_ENV", "qa"),  # CLI flag wins, then the env var, then a default
        choices=["local", "qa", "staging", "prod"],
        help="Target environment (strategy) for the run",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Runs once after collection: a central place for run-wide rules.

    Rule 1 (safety): tests marked creates_data are SKIPPED on an env that forbids data changes.
    Rule 2 (convenience): any test whose file name contains "api" gets the api marker for free.
    """
    env = get_environment(config.getoption("--env", default=os.getenv("TEST_ENV", "qa")))
    skip_prod = pytest.mark.skip(reason=f"{env.name} does not allow data changes")
    for item in items:
        if not env.allow_data_changes and item.get_closest_marker("creates_data"):
            item.add_marker(skip_prod)
        if "api" in item.path.name:
            item.add_marker(pytest.mark.api)


# ── FIXTURES ───────────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def env_config(pytestconfig: pytest.Config) -> EnvironmentConfig:
    """Session scope = once per run (per xdist WORKER when run in parallel)."""
    return get_environment(pytestconfig.getoption("--env", default=os.getenv("TEST_ENV", "qa")))


@pytest.fixture(scope="session")
def ae_server() -> Iterator[FakeAutomationExerciseServer]:
    """Expensive shared resource → session scope. Real life: a requests.Session / APIRequestContext."""
    server = FakeAutomationExerciseServer()  # SETUP (once)
    yield server  # ← every test that needs it runs here
    server.users.clear()  # TEARDOWN (once, after the last test)


@pytest.fixture
def api_client(ae_server: FakeAutomationExerciseServer) -> ApiClient:
    return ApiClient(ae_server)  # function scope (default): fresh per test, cheap


@pytest.fixture
def products_api(api_client: ApiClient) -> ProductsApi:
    return ProductsApi(api_client)  # composition: service HAS a client


@pytest.fixture
def account_api(api_client: ApiClient) -> AccountApi:
    return AccountApi(api_client)


@pytest.fixture
def auth_api(api_client: ApiClient) -> AuthApi:
    return AuthApi(api_client)


@pytest.fixture
def registered_user(account_api: AccountApi) -> Iterator[NewUser]:
    """TS registeredUser: create → yield to the test → ALWAYS delete (even if the test failed)."""
    user = build_user()  # 1. unique, valid data
    expect_api_code(account_api.create(user), 201, "User created!")  # 2. real account, proven
    yield user  # 3. ← THE TEST RUNS HERE
    account_api.delete(user.email, user.password)  # 4. teardown, runs on pass AND fail


@pytest.fixture
def make_user(account_api: AccountApi) -> Iterator[Callable[..., NewUser]]:
    """FACTORY-AS-FIXTURE: when one test needs SEVERAL users. Cleans up every one it made."""
    created: list[NewUser] = []

    def _make(**overrides: str) -> NewUser:
        user = build_user(**overrides)
        expect_api_code(account_api.create(user), 201)
        created.append(user)
        return user

    yield _make
    for user in created:  # a plain for loop: each delete finishes before the next
        account_api.delete(user.email, user.password)


@pytest.fixture(autouse=True)
def _count_requests_per_test(ae_server: FakeAutomationExerciseServer, request: pytest.FixtureRequest) -> Iterator[None]:
    """AUTOUSE: runs for EVERY test without being requested (TS: { auto: true }).
    Here it records how many API calls each test made, on the test node, for reporting."""
    before = ae_server.request_count
    yield
    request.node.user_properties.append(("api_requests", ae_server.request_count - before))  # → junit xml
