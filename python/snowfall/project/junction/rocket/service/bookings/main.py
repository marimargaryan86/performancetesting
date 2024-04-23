import ipaddress
import random
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.junction.rocket.service.bookings import (
    amqp,
    bookings,
    cancellations,
    grpc,
    importer,
    repository,
)
from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    bookings_pb2_grpc,
    meta_pb2_grpc,
)
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    httpx_factory,
)
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.zendesk import client


class _BookingSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    mongo_dsn: Sequence[pydantic.AnyUrl]


class _GrpcSettings(_BookingSettings, application.Settings):
    default_page_size: int = 100
    gateway_address: str
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class _TicketEventsConsumerSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    orders_address: str


class _CancellationsConsumerSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    mongo_dsn: Sequence[pydantic.AnyUrl]
    zendesk_cancellation_group_id: int
    zendesk_base_url: pydantic.AnyUrl
    zendesk_api_key: str
    gateway_address: str


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    booking_repository = repository.BookingRepository(
        collection=mongo.bookings.bookings,
    )

    gateway_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.gateway_address,
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.BookingService(
                gateway_meta=meta_pb2_grpc.MetaServiceStub(
                    gateway_channel,
                ),
                booking_handler=bookings.BookingHandler(
                    gateway=bookings_pb2_grpc.BookingServiceStub(
                        gateway_channel,
                    ),
                    fallback_bookings=booking_repository,
                ),
                booking_repository=booking_repository,
                publisher=amqp.BookingProducer(
                    producer_obj=producer.Producer(
                        connection=amqp_connection,
                        exchange=types.Exchange("bookings"),
                    ),
                ),
                default_page_size=app.settings.default_page_size,
                environment=app.environment,
                cancellations=grpc.Cancellations(
                    repository=repository.BookingCancellationRepository(
                        collection=mongo.bookings.cancellations,
                    ),
                    task_producer=amqp.BookingCancellationTaskProducer(
                        producer_obj=producer.Producer(
                            connection=amqp_connection,
                            exchange=types.Exchange("bookings"),
                        ),
                    ),
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _import(app: application.Application[_BookingSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    booking_importer = importer.BookingImporter(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_bookings".format(app.name),
            binds=[(types.Exchange("bookings"), "bookings.results.prices")],
        ),
        booking_repository=repository.BookingRepository(
            mongo.bookings.bookings,
        ),
    )
    await booking_importer.consume()


async def _consume_cancellations(
    app: application.Application[_CancellationsConsumerSettings],
) -> None:
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    http_client = await httpx_factory.make_client(app)

    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    await cancellations.BookingCancellationsConsumer(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_cancellations".format(app.name),
            binds=[(types.Exchange("bookings"), "bookings.cancellations")],
        ),
        cancellation_handler=cancellations.CancellationHandler(
            gateway_stub=bookings_pb2_grpc.BookingServiceStub(
                await grpc_factory.make_insecure_channel(
                    app,
                    app.settings.gateway_address,
                ),
            ),
            bookings=repository.BookingRepository(
                collection=mongo.bookings.bookings,
            ),
            cancellations=repository.BookingCancellationRepository(
                collection=mongo.bookings.cancellations,
            ),
            manual_handler=cancellations.ManualCancellationHandler(
                zendesk_client=client.ZendeskClient(
                    base_url=str(app.settings.zendesk_base_url),
                    api_key=app.settings.zendesk_api_key,
                    http_client=http_client,
                    env=app.environment,
                ),
                group_id=app.settings.zendesk_cancellation_group_id,
            ),
        ),
    ).consume()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="junction-rocket-bookings")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        application.Command(
            name="import",
            callback=_import,
            settings_class=_BookingSettings,
        ),
        application.Command(
            name="consume-cancellations",
            callback=_consume_cancellations,
            settings_class=_CancellationsConsumerSettings,
        ),
    )
