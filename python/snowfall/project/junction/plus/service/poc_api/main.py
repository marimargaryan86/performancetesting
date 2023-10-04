import random
from functools import partial

import httpx
import openai
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.plus.service.poc_api import (
    ai_utils,
    bootstrap,
    flight_stats_client,
    handlers,
    icoupon,
    repository,
    s3,
    travel_fusion,
    twilio,
)
from snowfall.project.junction.plus.service.poc_api.routes import router
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.http import auth
from snowfall.vendor.junction.go import client


async def _http(app: application.AsyncApplication[bootstrap.Settings]) -> None:
    openai.api_key = app.settings.openai_api_key
    junction_client = client.Client(
        base_url=app.settings.junction_api_address,
        auth=auth.TokenAuth(app.settings.junction_api_token),
    )
    fs_client = flight_stats_client.FlightStatusClient(
        api_url=app.settings.flight_stats_api_address,
        app_id=app.settings.flight_stats_app_id,
        app_key=app.settings.flight_stats_app_key,
    )
    s3_client = s3.S3Client(
        app.settings.aws_access_key,
        app.settings.aws_secret_key,
    )
    icoupon_client = icoupon.ICouponClient(
        api_url=app.settings.icoupon_api_address,
        client_id=app.settings.icoupon_client_id,
        client_secret=app.settings.icoupon_client_secret,
    )
    tf_client = travel_fusion.TravelFusionClient(
        api_url=app.settings.tf_api_address,
        client_key=app.settings.tf_client_key,
    )
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )[app.settings.mongo_db]
    redis_client = redis.Client[str](
        aioredis.from_url(
            str(random.choice(app.settings.redis_dsn)),  # noqa: S311
            decode_responses=True,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
        prefix=app.name,
    )

    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                junction_client=junction_client,
                redis_client=redis_client,
                fs_client=fs_client,
                icoupon_client=icoupon_client,
                s3_client=s3_client,
                tf_client=tf_client,
                ai_bot=ai_utils.AIBot(),
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
    )
    asgi_app.add_exception_handler(
        httpx.HTTPStatusError,
        partial(
            handlers.go_status_error_handler,
            go_urls=[app.settings.junction_api_address],
        ),
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="plus-poc-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
    )
