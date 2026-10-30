# conftest.py
# SESSION scope lives here so EVERY test file can share it.
# A session fixture is created ONCE for the whole `pytest` run and destroyed after the LAST test.
import pytest

BROWSER_LAUNCHES = {"count": 0}          # counts how many times the browser was launched


@pytest.fixture(scope="session")
def browser():
    """Real-world use: launching a browser is slow (1-3 s), so do it ONCE per run.
    Other session examples: loading config/env, getting an auth token, starting a mock server."""
    BROWSER_LAUNCHES["count"] += 1
    print(f"\n  🌐 [SESSION setup]    launch browser (launch #{BROWSER_LAUNCHES['count']})")
    session_browser = {"name": "chromium", "launch_number": BROWSER_LAUNCHES["count"], "pages_opened": 0}
    yield session_browser
    print(f"\n  🌐 [SESSION teardown] close browser after {session_browser['pages_opened']} pages")