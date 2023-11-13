import datetime

import freezegun
import pytest

from snowfall.stdlib import time


@pytest.mark.parametrize(
    ("date_of_birth", "expected_age"),
    [
        (datetime.date(1990, 10, 24), 32),
        (datetime.date(1990, 10, 25), 32),
        (datetime.date(1990, 10, 26), 31),
    ],
)
@freezegun.freeze_time("2022-10-25")
def test_date_to_age(
    date_of_birth: datetime.date,
    expected_age: int,
) -> None:
    assert time.date_to_age(date_of_birth) == expected_age


@pytest.mark.parametrize(
    ("at_date", "date_of_birth", "expected_age"),
    [
        (datetime.date(2022, 10, 25), datetime.date(1990, 10, 25), 32),
        (datetime.date(2022, 9, 25), datetime.date(1990, 10, 25), 31),
        (datetime.date(2022, 11, 25), datetime.date(1990, 10, 25), 32),
    ],
)
@freezegun.freeze_time("2000-01-01")
def test_age_is_correct_with_custom_date(
    at_date: datetime.date,
    date_of_birth: datetime.date,
    expected_age: int,
) -> None:
    assert time.date_to_age(date_of_birth, at_date) == expected_age
