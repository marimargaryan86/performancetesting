from collections.abc import Sequence
from datetime import date

import freezegun
import pytest

from snowfall.project.junction.rocket.service.api.models import Passenger
from snowfall.project.junction.rocket.service.api.passengers import (
    passengers_to_fake_user_ids,
)


@pytest.mark.parametrize(
    ("context", "dobs", "expected"),
    [
        ("empty list", [], []),
        ("clear adult", [date(2001, 1, 1)], [-10]),
        ("last day for adult", [date(2002, 1, 1)], [-10]),
        ("first day for child", [date(2002, 1, 2)], [-11]),
        ("same day", [date(2020, 1, 1)], [-12]),
        (
            "one of each",
            [date(2001, 1, 1), date(2012, 1, 1), date(2018, 12, 1)],
            [-10, -11, -12],
        ),
        (
            "three adults",
            [
                date(2001, 1, 1),
                date(2012, 1, 1),
                date(2001, 1, 1),
                date(2001, 10, 1),
                date(2018, 12, 1),
            ],
            [-10, -11, -20, -30, -12],
        ),
    ],
    ids=lambda xx: xx,
)
@freezegun.freeze_time("2020-01-01")
def test_fake_users(
    context: str,
    dobs: Sequence[date],
    expected: Sequence[int],
) -> None:
    passengers = [Passenger(date_of_birth=da) for da in dobs]
    assert passengers_to_fake_user_ids(passengers) == expected
