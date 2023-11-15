from collections.abc import Mapping, Sequence

import pytest

from snowfall.stdlib.format import jsonapi


@pytest.mark.parametrize(
    ("resource", "expected"),
    [
        (
            {
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
            {
                "departureAfter": "1957-04-30T08:34:00.826Z",
                "arrivalBefore": "1947-08-17T08:12:02.822Z",
                "origin": "8c3e06ac-1c17-986c-9510-c35229954f7c",
                "destination": "78a77e1e-cc51-b08b-1fe5-a75349cb73b1",
            },
        ),
        (
            {
                "attributes": {},
                "relationships": {
                    "trips": {
                        "data": [
                            {
                                "id": "8c3e06ac-1c17-986c-9510-c35229954f7c",
                                "type": "trips",
                            },
                            {
                                "id": "76f1cdcc-32d2-47ac-b715-67c495b90e00",
                                "type": "trips",
                            },
                        ],
                    },
                },
                "type": "offers-trip-searches",
            },
            {
                "trips": [
                    "8c3e06ac-1c17-986c-9510-c35229954f7c",
                    "76f1cdcc-32d2-47ac-b715-67c495b90e00",
                ],
            },
        ),
        (
            {
                "attributes": {},
                "relationships": {
                    "foo": {
                        "data": None,
                    },
                },
                "type": "foo",
            },
            {
                "foo": None,
            },
        ),
        (
            {
                "attributes": {},
                "relationships": {
                    "foo": {
                        "data": [],
                    },
                },
                "type": "foo",
            },
            {
                "foo": [],
            },
        ),
    ],
)
def test_resource_is_flattened(
    resource: jsonapi.Resource,
    expected: Mapping[str, object | str | Sequence[str] | None],
) -> None:
    assert jsonapi.flatten_resource(resource) == expected
