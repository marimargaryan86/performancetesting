import operator
from typing import Any, Mapping, Optional

import pytest

from snowfall.junction.client_api import request_helpers


@pytest.mark.parametrize(
    "request_data, expected",
    [
        (
            {
                "data": {
                    "attributes": {
                        "departureAfter": "1957-04-30T08:34:00.826Z",
                        "arrivalBefore": "1947-08-17T08:12:02.822Z",
                    },
                    "relationships": {
                        "origin": {
                            "data": {
                                "id": "8c3e06ac-1c17-986c-9510-c35229954f7c",
                                "type": "places",
                            },
                        },
                        "destination": {
                            "data": {
                                "id": "78a77e1e-cc51-b08b-1fe5-a75349cb73b1",
                                "type": "places",
                            },
                        },
                    },
                    "type": "trip-searches",
                },
            },
            {
                "departureAfter": "1957-04-30T08:34:00.826Z",
                "arrivalBefore": "1947-08-17T08:12:02.822Z",
                "origin": "8c3e06ac-1c17-986c-9510-c35229954f7c",
                "destination": "78a77e1e-cc51-b08b-1fe5-a75349cb73b1",
            },
        ),
        (
            {
                "data": {
                    "attributes": {},
                    "relationships": {
                        "trips": {
                            "data": [
                                {
                                    "id": "8c3e06ac-1c17-986c-9510-c35229954f7c",
                                    "type": "trips",
                                },
                            ],
                        },
                    },
                    "type": "offers-trip-searches",
                },
            },
            {
                "trips": [
                    "8c3e06ac-1c17-986c-9510-c35229954f7c",
                ],
            },
        ),
    ],
)
def test_request_is_flattened(
    request_data: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    assert request_helpers.flatten_request_body(request_data) == expected


async def test_sequence_paginator_empty() -> None:
    page = await request_helpers.sequence_paginator(
        sequence=[],
        limit=1,
    )

    assert not page.sequence


async def test_sequence_paginator_limit_over_length() -> None:
    page = await request_helpers.sequence_paginator(
        sequence=[1, 2, 3, 4],
        limit=3,
        cursor=2,
    )
    assert page.sequence == [3, 4]


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
    assert op(request_helpers.get_next_url(url, next_page_token, limit), expected)
