from __future__ import annotations

import asyncio
import types as std_types
import zoneinfo

import more_itertools
import structlog

from snowfall.project.junction.service.planner.v1alpha import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.service.trips import trips
from snowfall.project.junction.service.trips.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import consumer, types
from snowfall.stdlib.v1alpha import latlng_pb2


class _TripSearchContext(object):
    def __init__(
        self,
        repository: trips.TripSearchRepository,
        message: amqp_pb2.TripSearchTask,
    ) -> None:
        self._message = message
        self._repository = repository

    async def __aenter__(self) -> _TripSearchContext:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: std_types.TracebackType | None,
    ) -> bool:
        if exc_type:
            await self._repository.mark_as_failed(self._message.trip_search.id)

        return False


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.TripSearchTask],
        planner: planner_pb2_grpc.PlannerServiceStub,
        trip_search_repository: trips.TripSearchRepository,
        trip_repository: trips.TripRepository,
    ):
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._planner = planner
        self._trip_search_repository = trip_search_repository
        self._trip_repository = trip_repository

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.TripSearchTask],
    ) -> None:
        await self._trip_search_repository.mark_as_processing(
            message.body.trip_search.id,
        )

        origins = {
            (origin.coordinates.latitude, origin.coordinates.longitude)
            for origin in message.body.trip_search.origins
        }
        destinations = {
            (destination.coordinates.latitude, destination.coordinates.longitude)
            for destination in message.body.trip_search.destinations
        }

        if not origins or not destinations:
            return

        async with _TripSearchContext(self._trip_search_repository, message.body):
            response = await self._planner.SearchJourney(
                request=planner_pb2.SearchJourneyRequest(
                    origins=[
                        latlng_pb2.LatLng(
                            latitude=origin[0],
                            longitude=origin[1],
                        )
                        for origin in origins
                    ],
                    destinations=[
                        latlng_pb2.LatLng(
                            latitude=destination[0],
                            longitude=destination[1],
                        )
                        for destination in destinations
                    ],
                    departure_after=protobuf.datetime_to_protobuf_datetime(
                        protobuf.protobuf_to_datetime(
                            message.body.trip_search.departure_after,
                        ).astimezone(
                            zoneinfo.ZoneInfo(
                                more_itertools.first(
                                    message.body.trip_search.origins,
                                ).time_zone,
                            ),
                        ),
                    ),
                    allowed_segment_types=message.body.trip_search.allowed_segment_types,
                ),
            )

            await asyncio.gather(
                self._trip_repository.add_from_journey_search(response),
                self._trip_search_repository.add_results_from_journey_search(
                    message.body.trip_search,
                    response,
                ),
            )
