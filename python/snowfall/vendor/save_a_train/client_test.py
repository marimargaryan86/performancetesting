import datetime

import pytest
import pytest_httpx

from snowfall.vendor.save_a_train import client, enums, exceptions
from snowfall.vendor.save_a_train.models import request

_BASE_SEARCH_URL = "https://test_url/searches"
_ORIGIN = "SAT_NL_AM_GVFLE"
_DESTINATION = "SAT_NL_RO_LCHPY"
_TRIP_TYPE = 1
_PASSENGER_COUNT = 1
_DATE = "2023-07-02"
_EMAIL = "test%40snowfall.com"
_PASSWORD = "secret"


async def test_get_general_results_no_route(
    httpx_mock: pytest_httpx.HTTPXMock,
    save_a_train_client: client.SATClient,
) -> None:
    expected_error_message = "{'errors': ['This route is not allowed']}"
    httpx_mock.add_response(
        url="{0}/{1}/{2}?triptype={3}&passengers={4}&ddate={5}&rdate=&email={6}&password={7}".format(
            _BASE_SEARCH_URL,
            _ORIGIN,
            _DESTINATION,
            _TRIP_TYPE,
            _PASSENGER_COUNT,
            _DATE,
            _EMAIL,
            _PASSWORD,
        ),
        json=expected_error_message,
    )

    with pytest.raises(exceptions.SATValidationError) as excinfo:
        await save_a_train_client.search_api_client.get_general_search_results(
            request=request.GeneralSearchResultsRequest(
                origin_id=_ORIGIN,
                destination_id=_DESTINATION,
                trip_type=enums.TripType.one_way,
                number_of_passengers=_PASSENGER_COUNT,
                departure_date=datetime.date(2023, 7, 2),
            ),
        )

    assert str(excinfo.value) == expected_error_message  # noqa: WPS441


async def test_get_general_results_no_trains(
    httpx_mock: pytest_httpx.HTTPXMock,
    save_a_train_client: client.SATClient,
) -> None:
    expected_error_message = "{'message': 'No Trains today for this route'}"
    httpx_mock.add_response(
        url="{0}/{1}/{2}?triptype={3}&passengers={4}&ddate={5}&rdate=&email={6}&password={7}".format(
            _BASE_SEARCH_URL,
            _ORIGIN,
            _DESTINATION,
            _TRIP_TYPE,
            _PASSENGER_COUNT,
            _DATE,
            _EMAIL,
            _PASSWORD,
        ),
        json=expected_error_message,
    )

    with pytest.raises(exceptions.SATValidationError) as excinfo:
        await save_a_train_client.search_api_client.get_general_search_results(
            request=request.GeneralSearchResultsRequest(
                origin_id=_ORIGIN,
                destination_id=_DESTINATION,
                trip_type=enums.TripType.one_way,
                number_of_passengers=_PASSENGER_COUNT,
                departure_date=datetime.date(2023, 7, 2),
            ),
        )

    assert str(excinfo.value) == expected_error_message  # noqa: WPS441
