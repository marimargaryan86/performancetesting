import base64
import pathlib
import random
import tempfile
from collections.abc import Sequence

import httpx
import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.plus.adapter import configuration_vectors, subscribers
from snowfall.project.junction.plus.notification_channels import (
    http_webhook,
    push_notification,
    whatsapp,
)
from snowfall.project.junction.plus.service.notification_center import importer, states
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory, application, grpc_factory
from snowfall.stdlib.transport.amqp import consumer, types


def cert_tmp_path(cert_base64: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(base64.b64decode(cert_base64))

        return tmp_file.name


class _ImportSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    notifications_address: str
    twilio_sid: str
    twilio_token: str
    firebase_key: str
    redis_dsn: Sequence[pydantic.AnyUrl]
    redis_prefix: str


async def _import(app: application.Application[_ImportSettings]) -> None:
    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    logging.register(http_client)
    metrics.register(http_client)
    notifications_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.notifications_address,
    )
    redis_client = redis.Client[str](
        aioredis.from_url(
            str(random.choice(app.settings.redis_dsn)),  # noqa: S311
            decode_responses=True,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
        prefix=app.settings.redis_prefix,
    )
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
        channels=states.Channels(
            whatsapp_channel=whatsapp.ProviderChannel(
                sid=app.settings.twilio_sid,
                token=app.settings.twilio_token,
                redis_client=redis_client,
                templates_root_path=pathlib.Path(),
            ),
            push_notification_channel=push_notification.ProviderChannel(
                credentials=cert_tmp_path(app.settings.firebase_key),
            ),
            http_webhook_channel=http_webhook.ProviderChannel(),
        ),
    )
    await notification_event_importer.consume()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="notification_center")

    entrypoint.enter_with_commands(
        application.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
    )
