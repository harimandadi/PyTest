# conftest.py: fixtures here are available to every test file in this folder (no import needed)
import pytest


@pytest.fixture(scope="session")
def base_url():
    """Level 8: shared config for the whole test run."""
    return "https://qa.example.com"


@pytest.fixture(autouse=True)
def log_test_name(request):
    """Level 7: autouse = runs for EVERY test automatically, without being requested."""
    print(f"\n▶ start {request.node.name}")
    yield
    print(f"■ end   {request.node.name}")