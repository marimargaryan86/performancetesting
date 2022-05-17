import datetime

import freezegun
import pytest

from snowfall.stdlib import time


@pytest.mark.parametrize(
    "current,date_of_birth,age",
    [
        (datetime.date(2022, 10, 25), datetime.date(1990, 10, 25), 32),
        (datetime.date(2022, 9, 25), datetime.date(1990, 10, 25), 31),
        (datetime.date(2022, 11, 25), datetime.date(1990, 10, 25), 32),
    ],
)
def test_date_to_age(
    current: datetime.date,
    date_of_birth: datetime.date,
    age: int,
) -> None:
    with freezegun.freeze_time(current):
        assert time.date_to_age(date_of_birth) == age
