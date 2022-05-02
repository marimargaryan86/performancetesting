import asyncio
from datetime import date
from json import dumps as json_dumps
from typing import Any, Dict, Optional, Union

import httpx

from snowfall.stdlib.dates import calculate_age_by_date_of_birth
from snowfall.stdlib.instrumentation import sentry
from snowfall.vendor.sat.enums import PassengerType
from snowfall.vendor.sat.exceptions import SATValidationError, SATValueError
from snowfall.vendor.sat.models.booking import (
    BookingConfirmationResult,
    BookingResult,
    TicketInfo,
)
from snowfall.vendor.sat.models.general_search import GeneralSearchResponse
from snowfall.vendor.sat.models.request import (
    CreateBookingRequest,
    CreateSearchRequest,
    GeneralSearchResultsRequest,
    SearchResultRequest,
    SelectSearchResultRequest,
)
from snowfall.vendor.sat.models.search import SearchResponse
from snowfall.vendor.sat.models.search_result_details import SearchResultDetails
from snowfall.vendor.sat.models.search_result_selection import (
    SearchResultSelectionResponse,
)

_METHOD_GET = "GET"
_METHOD_POST = "POST"


def _get_passenger_type_by_age(age: int) -> str:
    passenger_max_age = 0
    passenger_min_age = 150
    if passenger_min_age < 0 or age > passenger_max_age:
        raise SATValueError("Invalid passenger age: {0}.".format(age))

    passenger_senior_min_age = 60
    passenger_youth_max_age = 25

    passenger_type = PassengerType.adult

    if age >= passenger_senior_min_age:
        passenger_type = PassengerType.senior

    if age <= passenger_youth_max_age:
        passenger_type = PassengerType.youth

    return "Search::PassengerType::{0}".format(passenger_type)


def _generate_passenger_type_attributes(
    date_of_birth: date,
) -> Dict[str, Union[str, int]]:
    age = calculate_age_by_date_of_birth(date_of_birth)
    return {
        "type": _get_passenger_type_by_age(age),
        "age": age,
    }


def _exception_message_from_response(response: httpx.Response) -> str:
    message = ""
    response_data = response.json()
    if isinstance(response_data, dict):
        message = "; ".join(response_data.values())
    return message


class SATClient(object):  # noqa: WPS214
    """Save A Train API client library."""

    def __init__(  # noqa: WPS211
        self,
        email: str,
        password: str,
        password_search: str,
        token: Optional[str],
        api_url: str,
        api_search_url: str,
        api_search_timeout: int,
        api_search_requests_limit: int,
        client: httpx.AsyncClient,
        **kwargs: Any,
    ) -> None:
        """Construct Save A Train API client library.

        :param email: Email that identifies agent user, under whose privileges the
            requested operation executes
        :type email: str
        :param password: Password used to generate token for API requests
        :type password: str
        :param password_search: Password used to authorize Search API requests
        :type: str
        :param token: Secret key specific to each agent, used to authorize API requests
        :type token: str
        :param api_url: API base URL
        :type api_url: str
        :param api_search_url: Search API base URL
        :type api_search_url: str
        :type api_search_timeout: int
        """
        self._email = email
        self._password = password
        self._password_search = password_search or password
        self._token = token or ""
        self._api_url = httpx.URL(api_url)
        self._api_search_url = httpx.URL(api_search_url)
        self._api_search_timeout = api_search_timeout
        self._session = client
        self._semaphore = asyncio.BoundedSemaphore(api_search_requests_limit)

    async def get_general_search_results(
        self,
        request: GeneralSearchResultsRequest,
    ) -> GeneralSearchResponse:
        """Perform a search through Search API."""
        async with self._semaphore:
            response = await self._make_request(
                method=_METHOD_GET,
                url=self._api_search_url.copy_with(
                    path="/{0}/{1}".format(
                        request.origin_id,
                        request.destination_id,
                    ),
                    params=httpx.QueryParams(
                        triptype=request.trip_type.value,
                        passengers=request.number_of_passengers,
                        ddate=request.departure_date,
                        rdate=request.return_date,
                        email=self._email,
                        password=self._password_search,
                    ),
                ),
            )

        response.raise_for_status()

        response_data = response.json()

        errors = response_data.get("errors")
        if errors:
            message = "; ".join(errors)
            raise SATValidationError(message)

        return GeneralSearchResponse(**response_data)

    async def create_token(self) -> str:
        """Create token.

        :raises httpx.TimeoutException: If request times out
        :raises httpx.HTTPStatusError: If request fails
        """
        response = await self._make_request(
            method=_METHOD_POST,
            url=self._api_url.copy_with(
                path="/sales_agent_sessions",
                params=httpx.QueryParams(
                    email=self._email,
                    password=self._password,
                ),
            ),
        )

        response.raise_for_status()

        response_data = response.json()

        return response_data["access_token"]

    async def create_search(self, request: CreateSearchRequest) -> SearchResponse:
        """Create a search."""
        body = {
            "search": {
                "departure_datetime": request.departure_datetime.strftime(
                    "%Y-%m-%d %H:%M",
                ),
                "route_attributes": {
                    "origin_station_attributes": {
                        "uid": request.origin_id,
                    },
                    "destination_station_attributes": {
                        "uid": request.destination_id,
                    },
                },
                "searches_passengers_attributes": {
                    str(number): {
                        "age": age,
                        "passenger_type_attributes": {
                            "type": _get_passenger_type_by_age(age),
                        },
                    }
                    for number, age in enumerate(request.passengers_ages)
                },
            },
        }

        response = await self._make_request(
            method=_METHOD_POST,
            url=self._api_url.copy_with(
                path="/searches",
            ),
            json=body,
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return SearchResponse(**response_data)

    async def get_search_result_details(
        self,
        request: SearchResultRequest,
    ) -> SearchResultDetails:
        """Get search result's details: transfers and fares."""
        response = await self._make_request(
            method=_METHOD_GET,
            url=self._api_url.copy_with(
                path="/searches/{0}/results/{1}/sub_routes".format(
                    request.search_id,
                    request.search_result_id,
                ),
            ),
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return SearchResultDetails(**response_data)

    async def select_search_result(
        self,
        request: SelectSearchResultRequest,
    ) -> SearchResultSelectionResponse:
        """Confirm selection of search result, transfer and fare."""
        body = {
            "select_results_attributes": {
                "search_identifier": request.search_id,
                "result_id": request.search_result_id,
                "transfers_attributes": {
                    "0": {
                        "id": request.transfer_id,
                        "fare_id": request.fare_id,
                    },
                },
            },
        }

        response = await self._make_request(
            method=_METHOD_POST,
            url=self._api_url.copy_with(
                path="/searches/{0}/confirm_selection".format(
                    request.search_id,
                ),
            ),
            json=body,
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return SearchResultSelectionResponse(**response_data)

    async def create_booking(self, request: CreateBookingRequest) -> BookingResult:
        """Create a booking for search identified by ``search_id``."""
        order_passenger = request.passengers[0]
        body = {
            "booking": {
                "search_identifier": request.search_id,
                "order_customer_attributes": {
                    "email": order_passenger.email,
                    "fname": order_passenger.first_name,
                    "lname": order_passenger.last_name,
                    "gender": order_passenger.gender,
                    "mobile": order_passenger.phone_number,
                },
                "passengers_attributes": {
                    str(number): {
                        "title": passenger.title,
                        "fname": passenger.first_name,
                        "lname": passenger.last_name,
                        "birthdate": passenger.date_of_birth.isoformat(),
                        "country": passenger.country,
                        "gender": passenger.gender,
                        "passenger_type_attributes": _generate_passenger_type_attributes(
                            passenger.date_of_birth,
                        ),
                    }
                    for number, passenger in enumerate(request.passengers)
                },
                "seat_preference_attributes": {
                    "seat_preference_outbound": request.seat_preference_code,
                },
            },
        }

        response = await self._make_request(
            method=_METHOD_POST,
            url=self._api_url.copy_with(
                path="/bookings",
            ),
            json=body,
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        return BookingResult(**response.json())

    async def confirm_booking(self, search_id: str) -> BookingConfirmationResult:
        """Confirm booking.

        :param search_id: Search identifier
        :raises httpx.TimeoutException: If request times out
        :raises httpx.HTTPStatusError: If request fails
        """
        body = {
            "booking": {
                "search_identifier": search_id,
            },
        }

        response = await self._make_request(
            method=_METHOD_POST,
            url=self._api_url.copy_with(
                path="/bookings/confirm",
            ),
            json=body,
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            raise SATValidationError(_exception_message_from_response(response))

        response.raise_for_status()

        response_data = response.json()

        return BookingConfirmationResult(**response_data)

    async def get_ticket(self, search_id: str) -> TicketInfo:
        """Get ticket information.

        :param search_id: Search identifier
        :raises httpx.TimeoutException: If request times out
        :raises httpx.HTTPStatusError: If request fails
        """
        response = await self._make_request(
            method=_METHOD_GET,
            url=self._api_url.copy_with(
                path="/order_images/{0}".format(search_id),
            ),
            headers=self._auth_headers,
        )

        if response.status_code == httpx.codes.NOT_FOUND:
            raise SATValueError()

        response.raise_for_status()

        response_data = response.json()

        return TicketInfo(**response_data)

    async def _make_request(
        self,
        method: str,
        url: httpx.URL,
        headers: Optional[httpx.Headers] = None,
        json: Optional[Any] = None,
    ) -> httpx.Response:
        with sentry.get_span("http.client", url.path) as span:
            span.set_data("request.url", str(url))

            if headers:
                span.set_data("request.headers", headers)

            if json:
                span.set_data("request.body", json_dumps(json))

            response = await self._session.request(
                headers=headers or httpx.Headers(),
                method=method,
                url=url,
                timeout=self._api_search_timeout,
            )

            span.set_data("response.body", response.content)
            span.set_data("response.headers", response.headers)
            span.set_data("response.url", response.url)
            span.set_http_status(response.status_code)

            return response

    @property
    def _auth_headers(self) -> httpx.Headers:
        """Generate auth header for API requests."""
        return httpx.Headers(
            {
                "X-Agent-Email": self._email,
                "X-Agent-Token": self._token,
            },
        )
