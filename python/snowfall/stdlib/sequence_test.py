from snowfall.stdlib import sequence

_LIMIT = 2


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
