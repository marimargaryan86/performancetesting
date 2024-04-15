from collections.abc import Mapping
from itertools import starmap

import pytest
from starlette import requests

from snowfall.project.junction.hub.service.hub_api.filters import (
    get_journey_filters,
    get_reseller_filters,
)
from snowfall.project.junction.hub.service.hub_api.routes.go_orders import Journeys


@pytest.fixture()
def journey_query_params() -> Mapping[str, str]:
    return {
        "filter[createdAt][ge]": "2021-01-01",
        "filter[createdAt][le]": "2021-01-31",
        "filter[departureDate][ge]": "2021-01-01",
        "filter[departureDate][le]": "2021-01-31",
        "filter[status][eq]": "not-ticketed",
        "filter[pnr][eq]": "ABC123",
        "filter[passengerLastName][like]": "Smith",
    }


@pytest.fixture()
def resellers_query_params() -> Mapping[str, str]:
    return {
        "filter[name][like]": "Res 1",
    }


@pytest.fixture()
def journey_request_filters(
    journey_query_params: Mapping[str, str],
) -> requests.Request:
    query_string = "&".join(
        starmap("{0}={1}".format, journey_query_params.items()),
    )

    return requests.Request(scope={"query_string": query_string, "type": "http"})


@pytest.fixture()
def resellers_request_filters(
    resellers_query_params: Mapping[str, str],
) -> requests.Request:
    query_string = "&".join(
        starmap("{0}={1}".format, resellers_query_params.items()),
    )

    return requests.Request(scope={"query_string": query_string, "type": "http"})


async def test_get_journey_filters(
    journey_request_filters: requests.Request,
) -> None:
    status_mapping = Journeys._status_mapping  # noqa:SLF001

    filters = get_journey_filters(
        request=journey_request_filters,
        status_mapping=status_mapping,
    )

    assert len(filters) == 7


async def test_get_resellers_filters(
    resellers_request_filters: requests.Request,
) -> None:
    filters = get_reseller_filters(
        request=resellers_request_filters,
    )

    assert len(filters) == 1
