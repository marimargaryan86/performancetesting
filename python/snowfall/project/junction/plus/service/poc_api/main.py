import random
from functools import partial
from typing import Callable

import httpx
from motor import motor_asyncio
from redis import asyncio as aioredis
from starlette import applications

from snowfall.project.junction.extensions.service.mobile_api import (
    handlers as mobile_handlers,
)
from snowfall.project.junction.plus.service.poc_api import (
    bootstrap,
    flight_stats_client,
    repository,
    twilio,
)
from snowfall.project.junction.plus.service.poc_api.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.junction.go import client


def _factory(
    app: service.Application[bootstrap.Settings],
) -> Callable[[], applications.Starlette]:
    def decorator() -> applications.Starlette:
        junction_client = client.Client(
            api_url=random.choice(app.settings.junction_api_address),  # nosec
            token=app.settings.junction_api_token,
        )
        fs_client = flight_stats_client.FlightStatusClient(
            api_url=random.choice(app.settings.flight_stats_api_address),  # nosec
            app_id=app.settings.flight_stats_app_id,
            app_key=app.settings.flight_stats_app_key,
        )
        mongo = motor_asyncio.AsyncIOMotorClient(
            app.settings.mongo_dsn,  # nosec
        )[app.settings.mongo_db]
        redis_client = redis.Client[str](
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=True,
            ).client(),
            prefix=app.name,
        )

        asgi_app = application.create_starlette_app(
            routes=router.get_routes(
                bootstrap.create_dependencies(
                    junction_client=junction_client,
                    redis_client=redis_client,
                    fs_client=fs_client,
                    twilio_client=twilio.TwilioClient(
                        sid=app.settings.twilio_sid,
                        token=app.settings.twilio_token,
                        sender=app.settings.twilio_sender,
                    ),
                    orders_repository=repository.OrdersRepository(
                        mongo["orders"],
                    ),
                    subscriptions_repository=repository.SubscriptionsRepository(
                        mongo["subscriptions"],
                    ),
                    delay_webhook_repository=repository.DelayWebhookRepository(
                        mongo["delay_webhook"],
                    ),
                ),
            ),
            openapi_path=filesystem.resource_path(
                "junction.plus_poc_api",
                "openapi.json",
            ),
            validate_response=app.settings.validate_responses_against_spec,
        )
        asgi_app.add_exception_handler(
            httpx.HTTPStatusError,
            partial(
                mobile_handlers.go_status_error_handler,
                go_urls=app.settings.junction_api_address,
            ),
        )
        return asgi_app

    return decorator


def _serve(app: service.Application[bootstrap.Settings]) -> None:
    application.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="plus-poc-api")

    entrypoint.enter_with_commands(
        service.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
