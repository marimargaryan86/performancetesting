import operator
from typing import Optional

import pytest

from snowfall.junction.client_api import pagination_helpers


def test_sequence_paginator_empty() -> None:
    pagination = pagination_helpers.Pagination(limit=1)
    page = pagination_helpers.sequence_paginator(
        sequence=[],
        pagination=pagination,
    )

    assert not page.sequence
    assert page.next_page_token is None


def test_sequence_paginator_limit_over_length() -> None:
    pagination = pagination_helpers.Pagination(cursor="2", limit=3)
    page = pagination_helpers.sequence_paginator(
        sequence=[1, 2, 3, 4],
        pagination=pagination,
    )
    assert page.sequence == [3, 4]
    assert page.next_page_token is None


@pytest.mark.parametrize(
    "url, next_page_token, limit, expected",
    (
        (
            "http://localhost:8000/trips/searches/53df9a43-1052-46e6-a9d5-83f7768a4377/trips",
            "token",
            10,
            "http://localhost:8000/trips/searches/53df9a43-1052-46e6-a9d5-83f7768a4377/trips?page%5Bcursor%5D=token&page%5Blimit%5D=10",
        ),
        (
            "http://localhost:8000/trips/searches/53df9a43-1052-46e6-a9d5-83f7768a4377/trips",
            "2",
            10,
            "http://localhost:8000/trips/searches/53df9a43-1052-46e6-a9d5-83f7768a4377/trips?page%5Bcursor%5D=2&page%5Blimit%5D=10",
        ),
        (
            "http://localhost:8000/trips/searches/53df9a43-1052-46e6-a9d5-83f7768a4377/trips",
            "",
            10,
            None,
        ),
        (
            "http://localhost:8000/trips/searches/53df9a43-1052-46e6-a9d5-83f7768a4377/trips",
            None,
            10,
            None,
        ),
    ),
)
def test_get_next_url(
    url: str,
    next_page_token: Optional[str],
    limit: int,
    expected: Optional[str],
) -> None:
    op = operator.is_ if expected is None else operator.eq
    pagination = pagination_helpers.Pagination(limit=limit)
    assert op(
        pagination_helpers.get_next_url(url, next_page_token, pagination)["next"],
        expected,
    )
