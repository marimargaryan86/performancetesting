import ipaddress
import random
from collections.abc import Sequence

import httpx
import pydantic
from motor import motor_asyncio

from snowfall.project.junction.go import pay_integration
from snowfall.project.junction.go.adapter import passenger_name_records
from snowfall.project.junction.go.service.gateway.v1 import bookings_pb2_grpc
from snowfall.project.junction.go.service.orders import bookings, importer, orders
from snowfall.project.junction.go.service.orders.amqp import OrderProducer
from snowfall.project.junction.go.service.orders.grpc import OrderService
from snowfall.project.junction.go.service.orders.pay_transactions import (
    PayTransactionCreator,
)
from snowfall.project.junction.go.service.orders.zendesk.client import ZendeskClient
from snowfall.project.junction.go.service.passenger_name_records.v1 import (
    passenger_name_records_pb2_grpc,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.service import amqp_factory, application
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import client, server
from snowfall.vendor.junction.auth import UserAuth
from snowfall.vendor.junction.pay.client import Client as PayClient


class _GrpcSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    default_page_size: int = 100
    gateway_address: str
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    passenger_name_records_address: str
    zendesk_base_url: pydantic.AnyUrl
    zendesk_api_key: str


class _ImportSettings(pay_integration.Settings, application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    mongo_dsn: Sequence[pydantic.AnyUrl]
    passenger_name_records_address: str
    use_pay_to_create_transaction: bool = False


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    passenger_name_records_client = passenger_name_records.GrpcClient(
        passenger_name_records=passenger_name_records_pb2_grpc.PassengerNameRecordServiceStub(
            client.create_channel(app.settings.passenger_name_records_address),
        ),
    )

    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    logging.register(http_client)
    metrics.register(http_client)

    zendesk_client = ZendeskClient(
        base_url=str(app.settings.zendesk_base_url),
        api_key=app.settings.zendesk_api_key,
        http_client=http_client,
        env=app.environment,
    )

    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    booking_repository = orders.BookingRepository(
        collection=mongo.orders.journeys,
    )

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
                booking_handler=bookings.BookingHandler(
                    gateway=bookings_pb2_grpc.BookingServiceStub(
                        client.create_channel(app.settings.gateway_address),
                    ),
                    fallback_bookings=booking_repository,
                ),
                booking_repository=booking_repository,
                booking_details=orders.BookingDetailsRepository(
                    collection=mongo.orders.journeys,
                ),
                cancellation_requests=orders.CancellationRequestsRepository(
                    collection=mongo.orders.cancellation_requests,
                ),
                publisher=OrderProducer(
                    producer_obj=producer.Producer(
                        connection=amqp_connection,
                        exchange=types.Exchange("orders"),
                    ),
                ),
                default_page_size=app.settings.default_page_size,
                zendesk_client=zendesk_client,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _import(app: application.Application[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    logging.register(http_client)
    metrics.register(http_client)

    booking_importer = importer.BookingImporter(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.result.offer")],
        ),
        booking_repository=orders.BookingRepository(
            mongo.orders.journeys,
        ),
        pay_transaction_creator=PayTransactionCreator(
            use_pay_to_create_transaction=app.settings.use_pay_to_create_transaction,
            pay_client=PayClient(
                base_url=str(app.settings.public_pay_api_dsn),
                auth=UserAuth(
                    str(app.settings.public_pay_admin_api_dsn),
                    app.settings.pay_admin_username,
                    app.settings.pay_admin_password,
                ),
                client=http_client,
            ),
        ),
    )
    await booking_importer.consume()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="orders")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        application.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
    )
