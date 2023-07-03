import pathlib

import httpx
import pydantic

from snowfall.project.junction.plus.adapter import configuration_vectors, subscribers
from snowfall.project.junction.plus.notification_channels.whatsapp import (
    ProviderChannel,
)
from snowfall.project.junction.plus.service.notification_center import importer
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.transport.amqp import consumer, types
from snowfall.stdlib.transport.grpc.client import create_channel


class _ImportSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    notifications_address: str
    twilio_sid: str
    twilio_token: str


async def _import(app: service.AsyncApplication[_ImportSettings]) -> None:
    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    connection = await app.stack.enter_async_context(
        types.Connection(
            app.settings.amqp_dsn,
        ),
    )

    logging.register(http_client)
    metrics.register(http_client)
    notifications_channel = create_channel(app.settings.notifications_address)
    notification_event_importer = importer.NotificationEventImporter(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="plus_{0}".format(app.name),
            binds=[(types.Exchange("plus_events"), "plus.events")],
        ),
        configuration_vectors=configuration_vectors.GrpcClient(
            configuration_vectors=notifications_pb2_grpc.ConfigurationVectorServiceStub(
                notifications_channel,
            ),
        ),
        subscribers=subscribers.GrpcClient(
            subscribers=notifications_pb2_grpc.SubscriberServiceStub(
                notifications_channel,
            ),
        ),
        whatsapp_provider=ProviderChannel(
            sid=app.settings.twilio_sid,
            token=app.settings.twilio_token,
            templates_root_path=pathlib.Path("."),
        ),
    )
    await notification_event_importer.consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="notification_center")

    entrypoint.enter_with_commands(
        service.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
    )
