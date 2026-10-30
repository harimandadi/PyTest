# FUNCTION scope (the default)
# The fixture is created BEFORE EACH test and destroyed AFTER EACH test.
# → every test gets a brand-new, independent copy. Safest choice: no test can affect another.
import pytest

CREATED = {"count": 0}


@pytest.fixture                                  # same as @pytest.fixture(scope="function")
def cart():
    """Real-world use: fresh test data per test (a new cart, a new user, a new page).
    Tests that CHANGE data should get their own copy."""
    CREATED["count"] += 1
    print(f"\n  🛒 [FUNCTION setup]    new empty cart #{CREATED['count']}")
    shopping_cart = {"number": CREATED["count"], "items": []}
    yield shopping_cart
    print(f"\n  🛒 [FUNCTION teardown] delete cart #{shopping_cart['number']}")


def test_add_one_item(cart):
    cart["items"].append("laptop")
    assert cart["number"] == 1                   # first cart
    assert cart["items"] == ["laptop"]


def test_cart_starts_empty_again(cart):
    assert cart["number"] == 2                   # a NEW cart was created for this test
    assert cart["items"] == []                   # the laptop from the previous test is NOT here


def test_third_test_gets_third_cart(cart):
    assert cart["number"] == 3                   # created once PER TEST → 3 tests = 3 carts