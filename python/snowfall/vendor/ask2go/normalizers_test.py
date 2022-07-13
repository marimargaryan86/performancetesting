import datetime

import pytest

from snowfall.vendor.ask2go import normalizers


@pytest.mark.parametrize(
    "duration,expected",
    [
        ("12:00:00", datetime.timedelta(hours=12)),
        ("25:12:00", datetime.timedelta(hours=25, minutes=12)),
        (
            "25:12:55",
            datetime.timedelta(hours=25, minutes=12, seconds=55),
        ),
        (
            "1.25:12:55",
            datetime.timedelta(days=1, hours=25, minutes=12, seconds=55),
        ),
        (
            "12.25:12:55",
            datetime.timedelta(days=12, hours=25, minutes=12, seconds=55),
        ),
    ],
)
def test_normalize_duration(duration: str, expected: datetime.timedelta) -> None:
    assert normalizers.normalize_duration(duration) == expected


@pytest.mark.parametrize(
    "duration",
    [
        "12:00:00:00",
        "12:00:00.00",
        "1.1.12:00:00",
    ],
)
def test_invalid_duration(duration: str) -> None:
    with pytest.raises(ValueError):
        normalizers.normalize_duration(duration)
