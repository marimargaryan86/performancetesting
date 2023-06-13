import asyncio
import datetime
import time
from collections.abc import AsyncGenerator, Generator, Sequence
from typing import Any

import structlog
import tenacity

from snowfall.vendor.direct_ferries import client, errors
from snowfall.vendor.direct_ferries.models import operator, passenger, route, timetable

_logger = structlog.get_logger(__name__)
_DAYS_IN_YEAR = 365
_DEFAULT_REQUEST_DATE_INTERVAL_DAYS = 30


async def _request_by_chunks(  # noqa: WPS210
    requests: Sequence[Sequence[Any]],
    requests_per_second: int = 59,
) -> Sequence[Any]:
    response_data = []

    for index in range(0, len(requests), requests_per_second):
        start_time = time.perf_counter()
        responses = await asyncio.gather(
            *[
                tenacity.retry(
                    retry=tenacity.retry_if_exception_type(errors.DFServiceError),
                    stop=tenacity.stop_after_attempt(3),
                )(request_details[0])(*request_details[1])
                for request_details in requests[index : index + requests_per_second]
            ],
            return_exceptions=True,
        )

        for response in responses:
            if isinstance(response, tenacity.RetryError):
                _logger.error(
                    "Request failed",
                    exception=response,
                )
            else:
                response_data.append(response)

        time_spent = time.perf_counter() - start_time

        if time_spent < 1:
            await asyncio.sleep(1 - time_spent)

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


async def routes_for_operators(  # noqa: WPS231
    df_client: client.DfClient,
    operators: Sequence[operator.Operator],
) -> AsyncGenerator[route.Route, None]:
    route_responses: Sequence[route.RouteResponse] = await _request_by_chunks(
        [
            [df_client.routes.get_routes_by_operator, [operator_obj.identifier]]
            for operator_obj in operators
        ],
    )
    seen = set()

    for route_res in route_responses:
        for route_ob in route_res.route_data.routes:
            if not route_ob.port_from.code.strip() or not route_ob.port_to.code.strip():
                _logger.warning(
                    "Skipping incomplete port",
                    from_port_code=route_ob.port_from.code,
                    to_port_code=route_ob.port_to.code,
                )
                continue

            if route_ob.route_id not in seen:
                seen.add(route_ob.route_id)
                yield route_ob


async def timetables_from_routes(
    df_client: client.DfClient,
    routes: Sequence[route.Route],
    request_date_interval: datetime.timedelta | None = None,
) -> Sequence[timetable.TimetableResponse]:
    if not request_date_interval:
        request_date_interval = datetime.timedelta(
            days=_DEFAULT_REQUEST_DATE_INTERVAL_DAYS,
        )

    current_datetime = datetime.datetime.now()

    return await _request_by_chunks(
        [
            [
                df_client.timetables.get_timetables,
                [route_obj, start_date, end_date],
            ]
            for route_obj in routes
            for start_date, end_date in _chunk_datetime_interval(
                current_datetime,
                current_datetime + datetime.timedelta(days=_DAYS_IN_YEAR),
                request_date_interval,
            )
        ],
    )


async def passenger_info_for_routes(
    df_client: client.DfClient,
    routes: Sequence[route.Route],
) -> list[passenger.RoutePassengerInfoExtended]:
    responses = await _request_by_chunks(
        [
            [
                df_client.routes.get_passenger_info_by_route_and_operator,
                [route_obj.operator_details.identifier, route_obj.route_id],
            ]
            for route_obj in routes
        ],
    )

    return [
        passenger.RoutePassengerInfoExtended(
            route_id=routes[idx].route_id,
            passenger_info=response,
        )
        for idx, response in enumerate(responses)
    ]
