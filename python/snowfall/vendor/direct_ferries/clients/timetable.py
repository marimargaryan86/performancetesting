import datetime
from typing import Sequence

import httpx

from snowfall.vendor.direct_ferries.clients import base


class TimetableClient(base.BaseClient):
    async def get_timetables(
        self,
        operator_id: int,
        route_id: int,
        date_from: datetime.date,
        date_to: datetime.date,
    ) -> Sequence[datetime.datetime]:
        response_data = (
            await self._make_request(
                request_details=base.RequestDetails(
                    method="get",
                    url="{0}/api/{1}/Timetables/operators/{2}/routes/{3}".format(
                        self._config.api_url,
                        self._config.api_version,
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

        timetables = response_data["data"]["timetables"]

        return [datetime.datetime.fromisoformat(date) for date in timetables]
