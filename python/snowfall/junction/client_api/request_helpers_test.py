import uuid

import pytest

from snowfall.junction.client_api import request_helpers


@pytest.mark.asyncio
async def test_request_is_flattened() -> None:
    request = {
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
    }
    expected = {
        "departureAfter": "1957-04-30T08:34:00.826Z",
        "arrivalBefore": "1947-08-17T08:12:02.822Z",
        "origin": uuid.UUID("8c3e06ac-1c17-986c-9510-c35229954f7c"),
        "destination": uuid.UUID("78a77e1e-cc51-b08b-1fe5-a75349cb73b1"),
    }
    assert await request_helpers.flatten_request_body(request) == expected
