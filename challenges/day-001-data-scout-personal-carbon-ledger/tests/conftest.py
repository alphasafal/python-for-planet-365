from __future__ import annotations

from datetime import UTC, datetime

import pytest


@pytest.fixture
def fixed_clock():
    def _clock() -> datetime:
        return datetime(2026, 8, 4, 17, 0, tzinfo=UTC)

    return _clock
