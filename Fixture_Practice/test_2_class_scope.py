# CLASS scope
# The fixture is created ONCE per test CLASS and shared by all tests inside that class.
# A different class gets its own new copy.
import pytest

LOGINS = {"count": 0}


@pytest.fixture(scope="class")
def logged_in_session():
    """Real-world use: log in once for a group of related tests (e.g. all 'Admin' tests),
    instead of logging in again before every single test."""
    LOGINS["count"] += 1
    print(f"\n  🔑 [CLASS setup]    log in (login #{LOGINS['count']})")
    session = {"login_number": LOGINS["count"], "token": f"token-{LOGINS['count']}"}
    yield session
    print(f"\n  🔑 [CLASS teardown] log out (login #{session['login_number']})")


class TestAdminPages:
    def test_dashboard(self, logged_in_session):
        assert logged_in_session["login_number"] == 1     # first login

    def test_users_page(self, logged_in_session):
        assert logged_in_session["login_number"] == 1     # SAME login reused inside this class


class TestReportsPages:
    def test_reports(self, logged_in_session):
        assert logged_in_session["login_number"] == 2     # NEW class → new login

    def test_export(self, logged_in_session):
        assert logged_in_session["token"] == "token-2"    # reused inside this class