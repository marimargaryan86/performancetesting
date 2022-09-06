import datetime

import httpx

from snowfall.vendor.direct_ferries.clients import base
from snowfall.vendor.direct_ferries.models.route import Route
from snowfall.vendor.direct_ferries.models.timetable import TimeTable, TimetableData


class TimetableClient(base.BaseClient):
    async def get_timetables(
        self,
        route: Route,
        date_from: datetime.date,
        date_to: datetime.date,
    ) -> TimeTable:
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

        operator_time_tables = response_data["data"]["operatorTimetables"]
        return TimeTable(
            timetables=[
                TimetableData(
                    departure_time=time_table_data["departureTime"],
                    arrival_time=time_table_data["arrivalTime"],
                    duration_in_minutes=time_table_data["durationInMinutes"],
                )
                for operator_time_table in operator_time_tables
                for time_table_data in operator_time_table["timetables"]
            ],
            route=route,
        )
