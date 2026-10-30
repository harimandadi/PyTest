import pytest

from calc import add, subtract, multiply

# def test_add_positive_numbers():
#     assert add(2,5) == 7

# def test_add_negative_numbers():
#     assert add(-2,-5) == -7
#     print(f"The add with negative number for -2 and -5 is -7")


@pytest.mark.parametrize("a,b,expected", [
    (2,5,7),
    (-2,-5,-7),
    (0,0,0)
])
def test_add(a, b, expected):
    assert add(a, b) == expected
    print(f"Test add has passed for input: {a}, {b} and expected result is {expected}")

@pytest.mark.parametrize("a,b,expected", [
    (2,5,7),
    (-2,-5,-7),
    (0,0,0)
],ids=["positive numbers", "negative numbers", "zero numbers"])
def test_add_id(a, b, expected):
    assert add(a, b) == expected
    print(f"Test add has passed for input: {a}, {b} and expected result is {expected}")

@pytest.mark.parametrize("a,b,expected", [
    pytest.param(2,5,7,id="positive numbers"),
    pytest.param(-2,-5,-7, id="negative numbers"),
    pytest.param(0,0,0, id="zero numbers")
])
def test_add_param(a, b, expected):
    assert add(a, b) == expected
    print(f"Test add has passed for input: {a}, {b} and expected result is {expected}")