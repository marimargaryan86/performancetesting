import datetime
import pathlib
import random

import openai
from redis import asyncio as aioredis
from starlette.middleware import Middleware
from twilio.request_validator import RequestValidator

from snowfall.project.junction.plus.adapter import (
    configuration_vectors,
    flight_delay_predictor,
    monitoring_rules,
    notification_event_publisher,
    orders,
    subscribers,
)
from snowfall.project.junction.plus.notification_channels.whatsapp import (
    ProviderChannel,
)
from snowfall.project.junction.plus.service.flight_prediction.v1 import (
    flight_prediction_pb2_grpc,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.plus_webhooks import (
    bootstrap,
    chatbot_handlers,
    middlewares,
    open_ai,
)
from snowfall.project.junction.plus.service.plus_webhooks.matrix_callbacks import (
    MatrixChatbot,
)
from snowfall.project.junction.plus.service.plus_webhooks.routes import router
from snowfall.project.junction.plus.service.plus_webhooks.shortener import (
    ShortenerClient,
)
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application, grpc_factory


async def _http(
    app: application.Application[bootstrap.Settings],
) -> None:
    ai_client = openai.AsyncOpenAI(
        api_key=app.settings.openai_api_key,
        organization=app.settings.openai_org,
    )
    notifications_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.notifications_address,
    )
    flight_prediction_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.flight_prediction_address,
    )
    redis_client = redis.Client[str](
        aioredis.from_url(
            str(
                random.choice(app.settings.redis_dsn),  # noqa: S311
            ),
            decode_responses=True,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
        prefix=app.settings.redis_prefix,
    )
    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                monitoring_rules_client=monitoring_rules.GrpcClient(
                    monitoring_rules=notifications_pb2_grpc.MonitoringRuleServiceStub(
                        notifications_channel,
                    ),
                ),
                subscribers_client=subscribers.GrpcClient(
                    subscribers=notifications_pb2_grpc.SubscriberServiceStub(
                        notifications_channel,
                    ),
                ),
                orders_client=orders.GrpcClient(
                    orders=notifications_pb2_grpc.OrderServiceStub(
                        notifications_channel,
                    ),
                ),
                configuration_vectors_client=configuration_vectors.GrpcClient(
                    configuration_vectors=notifications_pb2_grpc.ConfigurationVectorServiceStub(
                        notifications_channel,
                    ),
                ),
                notification_event_publisher_client=notification_event_publisher.GrpcClient(
                    notification_event_publisher=notifications_pb2_grpc.NotificationEventPublisherServiceStub(
                        notifications_channel,
                    ),
                ),
                message_handler=chatbot_handlers.MessageHandler(
                    redis_client=redis_client,
                    cache_ttl=datetime.timedelta(minutes=15),
                    ai_bot=open_ai.AIBot(ai_client=ai_client),
                    shortener_client=ShortenerClient(
                        shortener_url=app.settings.shortener_url,
                        shortener_domain=app.settings.shortener_domain,
                        shortener_key=app.settings.shortener_key,
                    ),
                    flight_predictions_client=flight_delay_predictor.GrpcClient(
                        flight_prediction_pb2_grpc.FlightPredictionServiceStub(
                            flight_prediction_channel,
                        ),
                    ),
                ),
                whatsapp_channel=ProviderChannel(
                    sid=app.settings.twilio_sid,
                    token=app.settings.twilio_token,
                    redis_client=redis_client,
                    templates_root_path=pathlib.Path(),
                ),
            ),
        ),
        custom_middlewares=[
            Middleware(
                middlewares.HmacHeaderMiddleware,
                secret_key=app.settings.flight_stats_app_key,
                twilio_validator=RequestValidator(app.settings.twilio_token),
            ),
        ],
        openapi_path=None,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


async def _serve(
    app: application.Application[bootstrap.Settings],
) -> None:
    ai_client = openai.AsyncOpenAI(
        api_key=app.settings.openai_api_key,
        organization=app.settings.openai_org,
    )
    notifications_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.notifications_address,
    )
    # TODO: Replace with snowfall.stdlib.service.redis_factory.make_client
    redis_client = redis.Client[str](
        aioredis.from_url(
            str(
                random.choice(app.settings.redis_dsn),  # noqa: S311
            ),
            decode_responses=True,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
        prefix=app.settings.redis_prefix,
    )
    matrix_chatbot = MatrixChatbot(
        homeserver=app.settings.matrix_homeserver_url,
        user=app.settings.matrix_user,
        redis_client=redis_client,
        subscribers_client=subscribers.GrpcClient(
            subscribers=notifications_pb2_grpc.SubscriberServiceStub(
                notifications_channel,
            ),
        ),
        configuration_vectors_client=configuration_vectors.GrpcClient(
            configuration_vectors=notifications_pb2_grpc.ConfigurationVectorServiceStub(
                notifications_channel,
            ),
        ),
        ai_bot=open_ai.AIBot(ai_client=ai_client),
        shortener_client=ShortenerClient(
            shortener_url=app.settings.shortener_url,
            shortener_domain=app.settings.shortener_domain,
            shortener_key=app.settings.shortener_key,
        ),
    )
    await matrix_chatbot.run_bot(app.settings.matrix_password)


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="plus-webhooks")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
        application.Command(
            name="serve",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
