@pytest.mark.parametrize("a, b, total", [
    (2, 3, 5),
    pytest.param(0.1, 0.2, 0.3, marks=pytest.mark.xfail(reason="float bug")),
])
def test_add(a, b, total):
    assert a + b == total