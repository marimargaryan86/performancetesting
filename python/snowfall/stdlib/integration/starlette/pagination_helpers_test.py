import operator

import pytest
from starlette import datastructures

from snowfall.stdlib.integration.starlette import pagination_helpers


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
            "http://localhost:8000/trips/searches/53df9a43-1052-46e6-a9d5-83f7768a4377/trips?page%5Bcursor%5D=&page%5Blimit%5D=10",
        ),
    ),
)
def test_get_next_url(
    url: str,
    next_page_token: str,
    limit: int,
    expected: str,
) -> None:
    pagination = pagination_helpers.Pagination(limit=limit)
    assert operator.eq(
        pagination_helpers.get_next_url(
            datastructures.URL(url),
            next_page_token,
            pagination,
        )["next"],
        expected,
    )
