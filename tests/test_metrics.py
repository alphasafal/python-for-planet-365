from planet365.metrics import percent_change, safe_divide


def test_safe_divide() -> None:
    assert safe_divide(10, 2) == 5
    assert safe_divide(10, 0) is None


def test_percent_change() -> None:
    assert percent_change(100, 80) == -20
    assert percent_change(0, 1) is None
