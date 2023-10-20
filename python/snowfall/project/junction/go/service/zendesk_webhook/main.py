import datetime

import pydantic

from snowfall.project.junction.go.service.zendesk_webhook.amqp import EventProducer
from snowfall.project.junction.go.service.zendesk_webhook.bootstrap import (
    create_dependencies,
)
from snowfall.project.junction.go.service.zendesk_webhook.router import get_routes
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.service import amqp_factory, application
from snowfall.stdlib.transport.amqp import producer, types


class _Settings(starlette.Settings):
    amqp_dsn: pydantic.AmqpDsn
    default_ttl: datetime.timedelta = datetime.timedelta(days=30)


async def _http(app: application.Application[_Settings]) -> None:
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    asgi_app = starlette.create_starlette_app(
        routes=get_routes(
            create_dependencies(
                event_producer=EventProducer(
                    producer=producer.Producer(
                        connection=amqp_connection,
                        exchange=types.Exchange("zendesk_webhook"),
                    ),
                    routing_key="zendesk_webhook.event",
                ),
            ),
        ),
        openapi_path=None,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="zendesk-webhook")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=_Settings,
        ),
    )
