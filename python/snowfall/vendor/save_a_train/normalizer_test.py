import datetime

import pytest

from snowfall.vendor.save_a_train import normalizers


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("2h22m", datetime.timedelta(hours=2, minutes=22)),
        (22, datetime.timedelta(seconds=22)),
        (22.0, datetime.timedelta(seconds=22)),
    ],
)
def test_normalizer(input_value: float | str, expected: datetime.timedelta) -> None:
    assert normalizers.normalize_time(input_value) == expected
