import abc
from typing import Sequence

import httpx

from snowfall.vendor.direct_ferries.clients import base
from snowfall.vendor.direct_ferries.models import passenger, route

_GET_METHOD = "get"
_DATA_KEY = "data"
_ROUTES_KEY = "routes"


class RouteClient(abc.ABC):
    @abc.abstractmethod
    async def get_routes_by_operator(self, operator_id: int) -> route.RouteResponse:
        """Get routes for a given operator."""


class RouteHttpClient(base.BaseClient, RouteClient):
    async def get_routes_by_country(self, country_iso: str) -> route.RouteResponse:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/countries/{2}/routes".format(
                        self._config.api_url,
                        self._config.api_version,
                        country_iso,
                    ),
                    query_params=httpx.QueryParams(**self._request_params),
                ),
            )
        ).json()

        return route.RouteResponse(**response_data)

    async def get_routes_by_coordinates(
        self,
        south_west_lat: str,
        south_west_lng: str,
        north_east_lat: str,
        north_east_lng: str,
    ) -> route.RouteResponse:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/routes/{2}/{3}/{4}/{5}".format(
                        self._config.api_url,
                        self._config.api_version,
                        south_west_lat,
                        south_west_lng,
                        north_east_lat,
                        north_east_lng,
                    ),
                    query_params=httpx.QueryParams(**self._request_params),
                ),
            )
        ).json()

        return route.RouteResponse(**response_data)

    async def get_routes_by_operator(self, operator_id: int) -> route.RouteResponse:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/operators/{2}/routes".format(
                        self._config.api_url,
                        self._config.api_version,
                        operator_id,
                    ),
                ),
            )
        ).json()

        return route.RouteResponse(**response_data)

    async def get_routes_by_port(self, port_code: str) -> route.RouteResponse:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/ports/{2}/routes".format(
                        self._config.api_url,
                        self._config.api_version,
                        port_code,
                    ),
                ),
            )
        ).json()

        return route.RouteResponse(**response_data)

    async def get_passenger_info_by_route_and_operator(
        self,
        operator_id: int,
        route_id: int,
    ) -> Sequence[passenger.RoutePassengerInfo]:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method=_GET_METHOD,
                    url="{0}/api/{1}/operators/{2}/routes/{3}/passengerinfo".format(
                        self._config.api_url,
                        self._config.api_version,
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
