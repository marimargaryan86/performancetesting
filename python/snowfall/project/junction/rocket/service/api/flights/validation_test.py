from typing import Any

import pytest

from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.api.flights.validation import (
    SearchRequestValidator,
)


def example_request() -> Any:
    return {
        "data": {
            "type": "flight-searches",
            "attributes": {
                "departureAfter": fixtures.DATETIME_TOMORROW.strftime(
                    "%Y-%m-%dT08:00:00.000Z",
                ),
                "passengers": [{"dateOfBirth": "1980-02-03"}],
            },
            "relationships": {
                "origin": {"data": {"id": fixtures.PLACES[0], "type": "places"}},
                "destination": {"data": {"id": fixtures.PLACES[1], "type": "places"}},
            },
        },
    }


def example_request_inbound() -> Any:
    return {
        "data": {
            "type": "flight-searches",
            "attributes": {
                "departureAfter": fixtures.DATETIME_TOMORROW.strftime(
                    "%Y-%m-%dT08:00:00.000Z",
                ),
                "returnAt": fixtures.DATETIME_AFTER_TOMORROW.strftime(
                    "%Y-%m-%dT08:00:00.000Z",
                ),
                "passengers": [{"dateOfBirth": "1980-02-03"}],
            },
            "relationships": {
                "selectedOutboundOffer": {
                    "data": {"id": fixtures.OFFERS[0], "type": "flight-offers"},
                },
                "origin": {"data": {"id": fixtures.PLACES[0], "type": "places"}},
                "destination": {"data": {"id": fixtures.PLACES[1], "type": "places"}},
            },
        },
    }


class TestRequestValidator:
    @pytest.mark.parametrize(
        "requests",
        [
            (example_request()),
            (example_request_inbound()),
        ],
    )
    async def test_request_validator(self, requests: Any) -> None:
        search_request_validator = SearchRequestValidator(requests)

        assert (
            not search_request_validator.validation_errors
        ), search_request_validator.as_json_api_response()
