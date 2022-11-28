import abc
import datetime

import httpx

from snowfall.vendor.direct_ferries.clients import base
from snowfall.vendor.direct_ferries.models import timetable
from snowfall.vendor.direct_ferries.models.route import Route


class TimetableClient(abc.ABC):
    @abc.abstractmethod
    async def get_timetables(
        self,
        route: Route,
        date_from: datetime.date,
        date_to: datetime.date,
    ) -> timetable.TimetableResponse:
        """Get timetables of the given route."""


class TimetableHttpClient(base.BaseClient, TimetableClient):
    async def get_timetables(
        self,
        route: Route,
        date_from: datetime.date,
        date_to: datetime.date,
    ) -> timetable.TimetableResponse:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method="get",
                    url="{0}/api/{1}/Timetables/routes/{2}".format(
                        self._config.api_url,
                        self._config.api_version,
                        route.route_id,
                    ),
                    query_params=httpx.QueryParams(
                        DateFrom=date_from.strftime("%Y-%m-%dT%H:%M:%S"),
                        DateTo=date_to.strftime("%Y-%m-%dT%H:%M:%S"),
                    ),
                ),
            )
        ).json()

        return timetable.TimetableResponse(**response_data, route=route)
