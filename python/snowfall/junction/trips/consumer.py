from typing import cast

from snowfall.junction.planner.v1 import planner_pb2, planner_pb2_grpc
from snowfall.junction.trips.v1alpha import amqp_pb2
from snowfall.transport import amqp


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        planner: planner_pb2_grpc.PlannerServiceStub,
    ):
        self._consumer = consumer
        self._planner = planner

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        body = cast(amqp_pb2.TripSearchTask, message.body)

        await self._planner.SearchJourney(  # type: ignore[misc]
            request=planner_pb2.SearchJourneyRequest(
                origin=body.trip_search.origin.coordinates,
                destination=body.trip_search.destination.coordinates,
                departure_after=int(
                    body.trip_search.departure_after.ToDatetime().timestamp(),
                ),
            ),
        )

        # todo: add results to database

        await message.ack()
