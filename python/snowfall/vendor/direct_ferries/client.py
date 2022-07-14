import dataclasses
import datetime
import inspect
from typing import Dict, Optional, Sequence

import httpx

from snowfall.vendor.direct_ferries import errors
from snowfall.vendor.direct_ferries.models import operator, passenger
from snowfall.vendor.direct_ferries.models import quote as quote_models
from snowfall.vendor.direct_ferries.models import request as request_models
from snowfall.vendor.direct_ferries.models import route, ticket

_DATA_KEY = "data"
_GET_METHOD = "get"
_POST_METHOD = "post"
_ROUTES_KEY = "routes"


@dataclasses.dataclass(frozen=True)
class _RequestDetails(object):
    url: str
    method: str
    payload: Optional[str] = None
    query_params: Optional[httpx.QueryParams] = None


@dataclasses.dataclass(frozen=True)
class AuthServiceResponse(object):
    token: str
    expires_at: datetime.datetime


class DFAuthClient(object):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_url: str,
        client_id: str,
        client_secret: str,
    ):
        self._http_client = http_client
        self._api_url = api_url.lstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret

    async def create_token(self) -> AuthServiceResponse:
        request_data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials",
        }

        start = datetime.datetime.now()

        response = await self._http_client.post(
            url="{0}/oauth2/token".format(self._api_url),
            data=request_data,
        )
        response.raise_for_status()
        response_data = response.json()

        expires_at = start + datetime.timedelta(seconds=response_data["expires_in"])

        return AuthServiceResponse(
            token=response_data["access_token"],
            expires_at=expires_at,
        )


class DFClient(object):  # noqa: WPS214
    """Direct Ferries API client library."""

    def __init__(  # noqa: WPS211
        self,
        http_client: httpx.AsyncClient,
        auth_client: DFAuthClient,
        client_id: str,
        client_secret: str,
        api_url: str,
        partner_code: str,
        timeout: int,
        api_version: Optional[str] = "v1.0",
    ) -> None:
        self._http_client = http_client
        self._auth_client = auth_client
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_url = api_url.lstrip("/")
        self._api_version = api_version
        self._partner_code = partner_code
        self._timeout = timeout

        self._auth_response: Optional[AuthServiceResponse] = None

    async def get_routes_by_country(self, country_iso: str) -> Sequence[route.Route]:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/countries/{2}/routes".format(
                        self._api_url,
                        self._api_version,
                        country_iso,
                    ),
                    query_params=httpx.QueryParams(**self._request_params),
                ),
            )
        ).json()

        return [
            route.Route(**route_data)
            for route_data in response_data[_DATA_KEY][_ROUTES_KEY]  # noqa: WPS204
        ]

    async def get_routes_by_coordinates(
        self,
        south_west_lat: str,
        south_west_lng: str,
        north_east_lat: str,
        north_east_lng: str,
    ) -> Sequence[route.Route]:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/routes/{2}/{3}/{4}/{5}".format(
                        self._api_url,
                        self._api_version,
                        south_west_lat,
                        south_west_lng,
                        north_east_lat,
                        north_east_lng,
                    ),
                    query_params=httpx.QueryParams(**self._request_params),
                ),
            )
        ).json()

        return [
            route.Route(**route_data)
            for route_data in response_data[_DATA_KEY][_ROUTES_KEY]
        ]

    async def get_routes_by_operator(self, operator_id: int) -> Sequence[route.Route]:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/operators/{2}/routes".format(
                        self._api_url,
                        self._api_version,
                        operator_id,
                    ),
                ),
            )
        ).json()

        return [
            route.Route(**route_data)
            for route_data in response_data[_DATA_KEY][_ROUTES_KEY]
        ]

    async def get_routes_by_port(self, port_code: str) -> Sequence[route.Route]:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/ports/{2}/routes".format(
                        self._api_url,
                        self._api_version,
                        port_code,
                    ),
                ),
            )
        ).json()

        return [
            route.Route(**route_data)
            for route_data in response_data[_DATA_KEY][_ROUTES_KEY]
        ]

    async def get_passenger_info_by_route_and_operator(
        self,
        operator_id: int,
        route_id: int,
    ) -> Sequence[passenger.RoutePassengerInfo]:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/operators/{2}/routes/{3}/passengerinfo".format(
                        self._api_url,
                        self._api_version,
                        operator_id,
                        route_id,
                    ),
                    query_params=httpx.QueryParams(**self._request_params),
                ),
            )
        ).json()

        route_passenger_info = response_data[_DATA_KEY]["routePassengerInfo"]

        return [
            passenger.RoutePassengerInfo(**passenger_information)
            for passenger_information in route_passenger_info
        ]

    async def get_timetables(
        self,
        operator_id: int,
        route_id: int,
        date_from: datetime.date,
        date_to: datetime.date,
    ) -> Sequence[datetime.datetime]:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/Timetables/operators/{2}/routes/{3}".format(
                        self._api_url,
                        self._api_version,
                        operator_id,
                        route_id,
                    ),
                    query_params=httpx.QueryParams(
                        DateFrom=date_from.strftime("%Y-%m-%dT%H:%M:%S"),
                        DateTo=date_to.strftime("%Y-%m-%dT%H:%M:%S"),
                    ),
                ),
            )
        ).json()

        timetables = response_data[_DATA_KEY]["timetables"]

        return [datetime.datetime.fromisoformat(date) for date in timetables]

    async def get_operators(self) -> Sequence[operator.Operator]:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/Operators".format(
                        self._api_url,
                        self._api_version,
                    ),
                ),
            )
        ).json()

        return [
            operator.Operator(**operator_data)
            for operator_data in response_data[_DATA_KEY]["operators"]
        ]

    async def get_quotes(
        self,
        request: request_models.QuoteRequest,
    ) -> Sequence[quote_models.Quote]:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_POST_METHOD,
                    url="{0}/api/{1}/Quotes/get-quotes-request".format(
                        self._api_url,
                        self._api_version,
                    ),
                    payload=request.json(by_alias=True),
                ),
            )
        ).json()

        return [
            quote_models.Quote(**quote_data)
            for quote_data in response_data[_DATA_KEY]["quotes"]
        ]

    async def get_accommodations(
        self,
        request: request_models.QuoteRequest,
    ) -> quote_models.AccommodationResponse:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_POST_METHOD,
                    url="{0}/api/{1}/Quotes/get-accommodation-request".format(
                        self._api_url,
                        self._api_version,
                    ),
                    payload=request.json(by_alias=True),
                ),
            )
        ).json()

        return quote_models.AccommodationResponse(**response_data[_DATA_KEY])

    async def get_ticket_types(
        self,
        request: request_models.QuoteRequest,
    ) -> ticket.TicketTypesResponse:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_POST_METHOD,
                    url="{0}/api/{1}/Quotes/get-ticket-types-request".format(
                        self._api_url,
                        self._api_version,
                    ),
                    payload=request.json(by_alias=True),
                ),
            )
        ).json()

        return ticket.TicketTypesResponse(**response_data[_DATA_KEY])

    async def generate_quote(
        self,
        request: request_models.QuoteRequest,
    ) -> quote_models.Quote:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    method=_POST_METHOD,
                    url="{0}/api/{1}/Quotes/generate-quote-request".format(
                        self._api_url,
                        self._api_version,
                    ),
                    payload=request.json(by_alias=True),
                ),
            )
        ).json()

        return quote_models.Quote(**response_data[_DATA_KEY]["quote"])

    async def save_quote(
        self,
        request: request_models.QuoteRequest,
    ) -> quote_models.Booking:
        response_data = (
            await self._make_request(
                request_details=_RequestDetails(
                    url="{0}/api/{1}/Quotes/save-quote-request".format(
                        self._api_url,
                        self._api_version,
                    ),
                    method=_POST_METHOD,
                    payload=request.json(by_alias=True),
                ),
            )
        ).json()

        return quote_models.Booking(**response_data[_DATA_KEY]["booking"])

    async def _make_request(
        self,
        request_details: _RequestDetails,
    ) -> httpx.Response:
        try:
            response = await self._http_client.request(
                method=request_details.method,
                url=request_details.url,
                content=request_details.payload,
                params=request_details.query_params,
                headers=await self._default_headers(),
            )
        except httpx.HTTPError as raw_exc:
            raise errors.ServiceError(inspect.getdoc(raw_exc)) from raw_exc

        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError(
                errors.get_response_error_message(response),
            ) from exc

        return response

    def _is_token_valid(self) -> bool:
        return bool(
            self._auth_response
            and self._auth_response.expires_at < datetime.datetime.now(),
        )

    async def _auth_token(self) -> str:
        if not self._is_token_valid():
            self._auth_response = await self._auth_client.create_token()

        return self._auth_response.token  # type: ignore[union-attr]

    async def _default_headers(self) -> Dict[str, str]:
        return {
            "content-type": "application/json",
            **await self._auth_headers(),
        }

    async def _auth_headers(self) -> Dict[str, str]:
        return {
            "Authorization": "Bearer {0}".format(await self._auth_token()),
        }

    @property
    def _request_params(self) -> Dict[str, str]:
        return {"culture": "en-GB"}
