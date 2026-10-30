import pytest;

@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
@pytest.mark.parametrize("viewport", ["mobile", "tablet", "desktop"])
def test_login_page(browser, viewport):
    print("Testing login page with browser:", browser)
    print("Viewport size is:", viewport)
    assert True

@pytest.mark.parametrize("browser", [
    pytest.param("chrome"),
    pytest.param("firefox"),
    pytest.param("edge"),
    pytest.param("safari", marks=pytest.mark.skip(reason="Safari is not supported at the moment"))
])
@pytest.mark.parametrize("viewport", ["mobile", "tablet", "desktop"])
def test_login_page_param(browser, viewport):
    print("Testing login page with browser:", browser)
    print("Viewport size is:", viewport)
    assert True