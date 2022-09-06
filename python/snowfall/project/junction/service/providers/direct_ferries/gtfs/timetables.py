import asyncio
from datetime import datetime
from typing import Any, Sequence

import pydantic

from snowfall.vendor.direct_ferries import client, errors
from snowfall.vendor.direct_ferries.models import operator, route, timetable

_LAST_MONTH_OF_YEAR = 12
_LAST_DAY_OF_YEAR = 31
_CURRENT_DATE = datetime.now().date()
_DURATION = 300


class Schedule(pydantic.BaseModel):
    operator_id: int
    route: route.Route
    timetables: Sequence[timetable.TimetableData]


class TimetableRepository(object):
    _requests_per_second = 40

    def __init__(self, df_client: client.DFClient) -> None:
        self._df_client = df_client

    async def get_timetables(self) -> Sequence[timetable.TimeTable]:
        operator_routes = await self._routes_for_operators(
            await self._df_client.operators.get_operators(),
        )

        return await self._timetables_from_routes(
            [route for routes in operator_routes for route in routes],
        )

    async def _routes_for_operators(
        self,
        operators: Sequence[operator.Operator],
    ) -> Sequence[Sequence[route.Route]]:
        return await self._request_by_chunks(
            [
                [self._df_client.routes.get_routes_by_operator, [operator.identifier]]
                for operator in operators
            ],
        )

    async def _timetables_from_routes(
        self,
        routes: Sequence[route.Route],
    ) -> Sequence[timetable.TimeTable]:
        return await self._request_by_chunks(
            [
                [
                    self._df_client.timetables.get_timetables,
                    [
                        route,
                        _CURRENT_DATE,
                        _CURRENT_DATE.replace(
                            month=_LAST_MONTH_OF_YEAR,
                            day=_LAST_DAY_OF_YEAR,
                        ),
                    ],
                ]
                for route in routes
            ],
        )

    async def _request_by_chunks(  # noqa: WPS210
        self,
        requests: Sequence[Sequence[Any]],
    ) -> Sequence[Any]:
        response_data = []
        failed = []

        for index in range(0, len(requests), self._requests_per_second):
            responses = await asyncio.gather(
                *[
                    request_details[0](*request_details[1])
                    for request_details in requests[
                        index : index + self._requests_per_second
                    ]
                ],
                return_exceptions=True,
            )

            for current_index, response in enumerate(responses):
                if isinstance(response, errors.DFTimeoutError):
                    failed.append(requests[index + current_index])
                else:
                    response_data.append(response)

            await asyncio.sleep(1)

        if failed:
            response_data.extend(await self._request_by_chunks(failed))

        return response_data
