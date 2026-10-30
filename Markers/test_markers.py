import pytest;
import os;


@pytest.mark.skip(reason="This feature is still under construction, so test is not required")
def test_marker_example():
    assert 1 == 1
    print("The test is to understand Marker")

@pytest.mark.xfail(reason="#Bug:28023 - This feature is failing to login the application")
def test_login_feature():
    assert 1 == 2
    print("The test is perform login operation")

@pytest.mark.smoke
@pytest.mark.regression
def test_setting_user():
    assert 1 == 1
    print("The user is created")


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.slow
def test_setting_admin_user():
    assert 1 == 1
    print("The admin user is created")


@pytest.mark.skipif(os.getenv("OPEN_AI_KEY") is not "", reason="This test cannot run as API key is not available in production environment")
def test_api_key():
    assert 1 == 1
    print("The API key is available")