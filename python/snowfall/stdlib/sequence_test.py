from collections.abc import Sequence
from typing import Any

import pytest

from snowfall.stdlib import sequence

_LIMIT = 2


@pytest.mark.parametrize(
    ("input_data", "expected"),
    [
        (["foobar"], ["foobar"]),
        (("foobar",), ("foobar",)),
        ("foobar", ["foobar"]),
        (b"foobar", [b"foobar"]),
    ],
)
def test_ensure(input_data: Any, expected: Sequence[Any]) -> None:
    assert sequence.ensure(input_data) == expected


def test_paginate() -> None:
    test_data = [1, 2, 3, 4]
    cursor = None

    for expected in ([1, 2], [3, 4], []):
        page = sequence.paginate(
            sequence=test_data,
            cursor=cursor,
            limit=2,
        )

        assert page.sequence == expected
        assert page.cursor != ""

        cursor = page.cursor
