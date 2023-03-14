import asyncio
import datetime
import os
from typing import Any, Generator, Sequence

import pydantic
import structlog
import tenacity

from snowfall.vendor.direct_ferries import client, errors
from snowfall.vendor.direct_ferries.models import operator, route, timetable

_CURRENT_DATETIME = datetime.datetime.now()
_REQUEST_DATE_INTERVAL_DAYS = 30
_REQUEST_DATE_INTERVAL = datetime.timedelta(days=_REQUEST_DATE_INTERVAL_DAYS)
_DAYS_IN_YEAR = 365
_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class Schedule(pydantic.BaseModel):
    operator_id: int
    route: route.Route
    timetables: Sequence[timetable.TimetableData]


class TimetableRepository(object):
    _requests_per_second = 50

    def __init__(self, df_client: client.DfClient) -> None:
        self._df_client = df_client
        self._logger = structlog.get_logger(__name__)

    async def get_timetables(self) -> Sequence[timetable.TimetableResponse]:
        operators = (
            await self._df_client.operators.get_operators()
        ).operator_data.operators

        routes = await self._routes_for_operators(operators)

        return await self._timetables_from_routes(
            [
                route
                for route in routes
                if route.port_from.code.strip() and route.port_to.code.strip()
            ],
        )

    async def _routes_for_operators(
        self,
        operators: Sequence[operator.Operator],
    ) -> Sequence[route.Route]:
        route_responses: Sequence[route.RouteResponse] = await self._request_by_chunks(
            [
                [self._df_client.routes.get_routes_by_operator, [operator.identifier]]
                for operator in operators
            ],
        )

        seen = set()
        unique_routes = []

        for route_res in route_responses:
            for route_obj in route_res.route_data.routes:
                if route_obj.route_id not in seen:
                    seen.add(route_obj.route_id)
                    unique_routes.append(route_obj)

        return unique_routes

    async def _timetables_from_routes(
        self,
        routes: Sequence[route.Route],
    ) -> Sequence[timetable.TimetableResponse]:
        return await self._request_by_chunks(
            [
                [
                    self._df_client.timetables.get_timetables,
                    [route, start_date, end_date],
                ]
                for route in routes
                for start_date, end_date in _chunk_datetime_interval(
                    _CURRENT_DATETIME,
                    _CURRENT_DATETIME + datetime.timedelta(days=_DAYS_IN_YEAR),
                    _REQUEST_DATE_INTERVAL,
                )
            ],
        )

    async def _request_by_chunks(
        self,
        requests: Sequence[Sequence[Any]],
    ) -> Sequence[Any]:
        response_data = []

        for index in range(0, len(requests), self._requests_per_second):
            responses = await asyncio.gather(
                *[
                    tenacity.retry(
                        retry=tenacity.retry_if_exception_type(errors.DFServiceError),
                        stop=tenacity.stop_after_attempt(3),
                    )(request_details[0])(*request_details[1])
                    for request_details in requests[
                        index : index + self._requests_per_second
                    ]
                ],
                return_exceptions=True,
            )

            for response in responses:
                if isinstance(response, tenacity.RetryError):
                    self._logger.error(
                        "Request failed",
                        exception=response,
                    )
                else:
                    response_data.append(response)

            await asyncio.sleep(1)

        return response_data


def _chunk_datetime_interval(
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    chunk_size: datetime.timedelta,
) -> Generator[tuple[datetime.datetime, datetime.datetime], None, None]:
    current = start_dt

    while current < end_dt:
        chunk_end_date = min(current + chunk_size, end_dt)
        yield current, chunk_end_date - datetime.timedelta(seconds=1)
        current = chunk_end_date
