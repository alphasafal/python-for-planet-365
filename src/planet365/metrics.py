from __future__ import annotations


def safe_divide(numerator: float, denominator: float) -> float | None:
    """Return numerator / denominator, or None when the denominator is zero."""
    if denominator == 0:
        return None
    return numerator / denominator


def percent_change(baseline: float, result: float) -> float | None:
    """Return percentage change from baseline to result.

    A zero baseline has no finite percentage change and therefore returns None.
    """
    ratio = safe_divide(result - baseline, abs(baseline))
    return None if ratio is None else ratio * 100.0
