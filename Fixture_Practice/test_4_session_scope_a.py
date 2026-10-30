# SESSION scope, file A
# The `browser` fixture comes from conftest.py (scope="session").
# It's created ONCE for the whole test run and shared by ALL files.


def test_open_login_page(browser):
    browser["pages_opened"] += 1
    assert browser["launch_number"] == 1        # first (and only) launch


def test_open_home_page(browser):
    browser["pages_opened"] += 1
    assert browser["launch_number"] == 1        # same browser reused