import datetime
import ipaddress
import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.junction.planner.v1alpha import planner_pb2_grpc
from snowfall.junction.trips import trips
from snowfall.junction.trips.consumer import TripSearchConsumer
from snowfall.junction.trips.grpc import TripSearchService, TripService
from snowfall.stdlib import service
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.grpc.client import create_channel

_TRIPS = "trips"


class _ConsumeSettings(service.Settings):
    amqp_dsn: Sequence[AnyUrl]
    planner_address: Sequence[str]
    mongo_dsn: Sequence[AnyUrl]


class _GrpcSettings(service.Settings):
    amqp_dsn: Sequence[AnyUrl]
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    trip_search_ttl: datetime.timedelta = datetime.timedelta(minutes=15)


async def _consume(app: service.Application[_ConsumeSettings]) -> None:
    connection = await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    )
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    async with connection:
        consumer = TripSearchConsumer(
            consumer=amqp.Consumer(
                connection=connection,
                exchange=amqp.Exchange(_TRIPS),
                queue_name="{0}_trip_searches_consumer".format(app.name),
                routing_key="trips.search",
            ),
            planner=planner_pb2_grpc.PlannerServiceStub(
                create_channel(
                    random.choice(app.settings.planner_address),  # nosec
                ),
            ),
            trip_search_repository=trips.TripSearchRepository(
                mongo[_TRIPS]["trip_searches"],
                datetime.timedelta(minutes=15),
            ),
            trip_repository=trips.TripRepository(mongo[_TRIPS][_TRIPS]),
        )

        await consumer.consume()


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    connection = await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    )
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    async with connection:
        producer = amqp.Producer(
            connection=connection,
            exchange=amqp.Exchange(_TRIPS),
        )
        grpc_server = server.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            [
                TripService(
                    segments=trips.SegmentRepository(mongo[_TRIPS][_TRIPS]),
                    trips_repository=trips.TripRepository(mongo[_TRIPS][_TRIPS]),
                    default_page_size=app.settings.default_page_size,
                ),
                TripSearchService(
                    repository=trips.TripSearchRepository(
                        mongo[_TRIPS]["trip_searches"],
                        app.settings.trip_search_ttl,
                    ),
                    producer=producer,
                ),
            ],
        )

        async with grpc_server.serve() as running:
            await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name=_TRIPS)

    entrypoint.enter_with_commands(
        service.Command(
            name="consume",
            callback=_consume,
            settings_class=_ConsumeSettings,
        ),
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
