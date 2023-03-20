import ipaddress
import random
from typing import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.junction.go.adapter import passenger_name_records
from snowfall.project.junction.service.orders import importer, orders
from snowfall.project.junction.service.orders.amqp import OrderProducer
from snowfall.project.junction.service.orders.grpc import OrderService
from snowfall.project.junction.service.passenger_name_records.v1alpha import (
    passenger_name_records_pb2_grpc,
)
from snowfall.stdlib import service
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import client, server


class _GrpcSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    passenger_name_records_address: Sequence[str]


class _ImportSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    mongo_dsn: Sequence[pydantic.AnyUrl]
    passenger_name_records_address: Sequence[str]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    passenger_name_records_client = passenger_name_records.GrpcClient(
        passenger_name_records=passenger_name_records_pb2_grpc.PassengerNameRecordServiceStub(
            client.create_channel(
                random.choice(app.settings.passenger_name_records_address),  # nosec
            ),
        ),
    )

    async with types.Connection(app.settings.amqp_dsn) as connection:
        grpc_server = server.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            [
                OrderService(
                    journeys=orders.JourneyRepository(
                        collection=mongo.orders.journeys,
                        passenger_name_records=passenger_name_records_client,
                    ),
                    orders=orders.OrderRepository(
                        collection=mongo.orders.journeys,
                    ),
                    bookings=orders.BookingRepository(
                        collection=mongo.orders.journeys,
                    ),
                    booking_details=orders.BookingDetailsRepository(
                        collection=mongo.orders.journeys,
                    ),
                    publisher=OrderProducer(
                        producer_obj=producer.Producer(
                            connection=connection,
                            exchange=types.Exchange("orders"),
                        ),
                    ),
                    default_page_size=app.settings.default_page_size,
                ),
            ],
        )

        async with grpc_server.serve() as running:
            await running.wait_for_termination()


async def _import(app: service.Application[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    async with types.Connection(app.settings.amqp_dsn) as connection:
        booking_importer = importer.BookingImporter(
            consumer_obj=consumer.Consumer(
                connection=connection,
                queue_name="{0}_orders".format(app.name),
                binds=[(types.Exchange("orders"), "orders.result.offer")],
            ),
            booking_repository=orders.BookingRepository(
                mongo.orders.journeys,
            ),
        )
        await booking_importer.consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="orders")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        service.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
    )
