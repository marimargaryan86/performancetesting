import datetime
import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl, BaseSettings

from snowfall.junction.planner.v1 import planner_pb2_grpc
from snowfall.junction.trips import trips
from snowfall.junction.trips.consumer import TripSearchConsumer
from snowfall.junction.trips.grpc import TripSearchService
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp, grpc

_TRIPS = "trips"


class _ConsumeSettings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    planner_address: Sequence[str]
    mongo_dsn: Sequence[AnyUrl]


class _GrpcSettings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    grpc_address: str = "[::]"
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    trip_search_ttl: datetime.timedelta = datetime.timedelta(minutes=15)


async def _consume(service: RunnableService) -> None:
    settings = _ConsumeSettings()
    connection = amqp.Connection(random.choice(settings.amqp_dsn))  # nosec
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec

    async with connection:
        consumer = TripSearchConsumer(
            consumer=await amqp.create_consumer(
                conn=connection,
                exchange_name=_TRIPS,
                queue_name="{0}_trip_searches_consumer".format(service.name),
                routing_key="trips.search",
            ),
            planner=planner_pb2_grpc.PlannerServiceStub(
                grpc.aio.insecure_channel(
                    random.choice(settings.planner_address),  # nosec
                ),
            ),
            repository=trips.TripSearchRepository(
                mongo[_TRIPS]["trip_searches"],
                datetime.timedelta(minutes=15),
            ),
        )

        await consumer.consume()


async def _serve(service: RunnableService) -> None:
    settings = _GrpcSettings()
    connection = amqp.Connection(random.choice(settings.amqp_dsn))  # nosec
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec

    async with connection:
        producer = await amqp.create_producer(
            conn=connection,
            exchange_name=_TRIPS,
        )
        server = grpc.create_server(
            settings.grpc_address,
            settings.grpc_port,
            [
                TripSearchService(
                    trips.TripSearchRepository(
                        mongo[_TRIPS]["trip_searches"],
                        settings.trip_search_ttl,
                    ),
                    producer,
                ),
            ],
        )

        await server.start()
        service.add_cleanup_task(server.stop(5))
        await server.wait_for_termination()


if __name__ == "__main__":
    _service = make_runnable_service(
        name=_TRIPS,
        tasks=(
            Task(command="consume", method=_consume),
            Task(command="grpc", method=_serve),
        ),
    )

    _service.run()
