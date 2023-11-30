import asyncio
import ipaddress
import random
from collections.abc import Sequence

import httpx
import pydantic
from motor import motor_asyncio

from snowfall.project.junction.go.adapter import orders as orders_adapter
from snowfall.project.junction.go.adapter import passenger_name_records
from snowfall.project.junction.go.service.gateway.v1 import bookings_pb2_grpc
from snowfall.project.junction.go.service.orders import bookings, importer, orders
from snowfall.project.junction.go.service.orders.amqp import OrderProducer
from snowfall.project.junction.go.service.orders.consumer import TicketEventConsumer
from snowfall.project.junction.go.service.orders.grpc import OrderService
from snowfall.project.junction.go.service.orders.pay_transactions import (
    PayTransactionCreator,
)
from snowfall.project.junction.go.service.orders.v1 import (
    orders_pb2_grpc,
)
from snowfall.project.junction.go.service.passenger_name_records.v1 import (
    passenger_name_records_pb2_grpc,
)
from snowfall.project.junction.go.service.resellers.v1 import resellers_pb2_grpc
from snowfall.project.pay.adapter import quotations, transactions
from snowfall.project.pay.adapter import refunds as refunds_adapter
from snowfall.project.pay.service.refunds.v1 import (
    grpc_pb2_grpc as refund_pb2_grpc,
)
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.service import amqp_factory, application, grpc_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.zendesk.client import ZendeskClient


class _GrpcSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    default_page_size: int = 100
    gateway_address: str
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    passenger_name_records_address: str
    resellers_address: str
    zendesk_base_url: pydantic.AnyUrl
    zendesk_api_key: str
    zendesk_cancellation_group_id: int
    refunds_address: str


class _ImportSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    mongo_dsn: Sequence[pydantic.AnyUrl]
    passenger_name_records_address: str
    use_pay_to_create_transaction: bool = False
    transactions_address: str


class _TicketEventsConsumerSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    orders_address: str


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    passenger_name_records_client = passenger_name_records.GrpcClient(
        passenger_name_records=passenger_name_records_pb2_grpc.PassengerNameRecordServiceStub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.passenger_name_records_address,
            ),
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

    resellers_channel, gateway_channel, refund_channel = await asyncio.gather(
        grpc_factory.make_insecure_channel(
            app,
            app.settings.resellers_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.gateway_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.refunds_address,
        ),
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            OrderService(
                journeys=orders.JourneyRepository(
                    collection=mongo.orders.journeys,
                    passenger_name_records=passenger_name_records_client,
                    resellers_client=resellers_pb2_grpc.ResellerServiceStub(
                        resellers_channel,
                    ),
                ),
                orders=orders.OrderRepository(
                    collection=mongo.orders.journeys,
                ),
                booking_handler=bookings.BookingHandler(
                    gateway=bookings_pb2_grpc.BookingServiceStub(
                        gateway_channel,
                    ),
                    fallback_bookings=booking_repository,
                ),
                booking_repository=booking_repository,
                booking_details=orders.BookingDetailsRepository(
                    collection=mongo.orders.journeys,
                ),
                booking_cancellations=orders.BookingCancellationsRepository(
                    collection=mongo.orders.cancellation_requests,
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
                cancellation_group_id=app.settings.zendesk_cancellation_group_id,
                refund_client=refunds_adapter.GrpcClient(
                    refund_pb2_grpc.RefundsServiceStub(
                        refund_channel,
                    ),
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _import(app: application.Application[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    transactions_channel = grpc_factory.make_insecure_channel(
        app,
        app.settings.transactions_address,
    )

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
            transactions_client=transactions.GrpcClient(
                transactions_pb2_grpc.TransactionsServiceStub(transactions_channel),
            ),
            quotations_client=quotations.GrpcClient(
                transactions_pb2_grpc.QuotationsServiceStub(transactions_channel),
            ),
        ),
    )
    await booking_importer.consume()


async def _consume_ticket_events(
    app: application.Application[_TicketEventsConsumerSettings],
) -> None:
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    orders_client = orders_adapter.GrpcClient(
        orders=orders_pb2_grpc.OrderServiceStub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.orders_address,
            ),
        ),
    )

    event_consumer = TicketEventConsumer(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_zendesk_events".format(app.name),
            binds=[(types.Exchange("zendesk_webhook"), "zendesk_webhook.event")],
        ),
        orders_client=orders_client,
    )
    await event_consumer.consume()


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
        application.Command(
            name="consume-ticket-events",
            callback=_consume_ticket_events,
            settings_class=_TicketEventsConsumerSettings,
        ),
    )
