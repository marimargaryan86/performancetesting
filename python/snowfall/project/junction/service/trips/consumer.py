import zoneinfo
from typing import cast

import structlog
from grpc import aio

from snowfall.project.junction.service.planner.v1alpha import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.service.trips import trips
from snowfall.project.junction.service.trips.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.v1alpha import latlng_pb2


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        planner: planner_pb2_grpc.PlannerServiceStub,
        trip_search_repository: trips.TripSearchRepository,
        trip_repository: trips.TripRepository,
    ):
        self._consumer = consumer
        self._logger = structlog.get_logger(__name__)
        self._planner = planner
        self._trip_search_repository = trip_search_repository
        self._trip_repository = trip_repository

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        body = cast(amqp_pb2.TripSearchTask, message.body)
        origins = {
            (origin.coordinates.latitude, origin.coordinates.longitude)
            for origin in body.trip_search.origins
        }
        destinations = {
            (destination.coordinates.latitude, destination.coordinates.longitude)
            for destination in body.trip_search.destinations
        }

        if not origins or not destinations:
            return

        try:
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
                            body.trip_search.departure_after,
                        ).astimezone(
                            zoneinfo.ZoneInfo(body.trip_search.origins[0].time_zone),
                        ),
                    ),
                ),
            )
        except aio.AioRpcError:
            self._logger.exception()
            await message.nack()

            return

        await self._trip_repository.add_from_journey_search(response)
        await self._trip_search_repository.add_results_from_journey_search(
            body.trip_search,
            response,
        )

        await message.ack()
