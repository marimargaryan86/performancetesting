from collections.abc import Sequence

import pytest

from snowfall.stdlib import sequence, string


@pytest.mark.parametrize(
    ("input_data", "expected"),
    [
        (["foobar"], ["foobar"]),
        (("foobar",), ("foobar",)),
        ("foobar", ["foobar"]),
        (b"foobar", [b"foobar"]),
    ],
)
def test_ensure(input_data: object, expected: Sequence[object]) -> None:
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


def test_to_and_from_composite_id() -> None:
    first_part = string.uuid()
    second_part = string.uuid()
    composite_id = sequence.to_composite_id([first_part, second_part])

    assert "=" not in composite_id

    parts = sequence.from_composite_id(composite_id)

    assert parts[0] == first_part
    assert parts[1] == second_part


def test_from_composite_id_with_invalid_id() -> None:
    with pytest.raises(sequence.InvalidCompositeError):
        sequence.from_composite_id("foobar")
