from typing import Any, Mapping

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
