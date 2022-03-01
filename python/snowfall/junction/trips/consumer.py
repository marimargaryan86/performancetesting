from typing import cast

import structlog
from grpc import aio

from snowfall.junction.planner.v1alpha import planner_pb2, planner_pb2_grpc
from snowfall.junction.trips import trips
from snowfall.junction.trips.v1alpha import amqp_pb2
from snowfall.transport import amqp


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

        try:
            response = await self._planner.SearchJourney(
                request=planner_pb2.SearchJourneyRequest(
                    origin=body.trip_search.origin.coordinates,
                    destination=body.trip_search.destination.coordinates,
                    departure_after=int(
                        body.trip_search.departure_after.ToDatetime().timestamp(),
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
