import datetime
import random
from collections.abc import Callable

import openai
from redis import asyncio as aioredis
from starlette.applications import Starlette
from starlette.middleware import Middleware
from twilio.request_validator import RequestValidator

from snowfall.project.junction.plus.adapter import (
    configuration_vectors,
    monitoring_rules,
    notification_event_publisher,
    orders,
    subscribers,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.plus_webhooks import (
    bootstrap,
    chatbot_handlers,
    middlewares,
)
from snowfall.project.junction.plus.service.plus_webhooks.routes import router
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc.client import create_channel


def _factory(
    app: application.Application[bootstrap.Settings],
) -> Callable[[], Starlette]:
    def decorator() -> Starlette:
        openai.api_key = app.settings.openai_api_key
        notifications_channel = create_channel(app.settings.notifications_address)
        return starlette.create_starlette_app(
            router.get_routes(
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
                        redis_client=redis.Client[str](
                            aioredis.from_url(
                                str(
                                    random.choice(app.settings.redis_dsn),  # noqa: S311
                                ),
                                decode_responses=True,
                                retry_on_error=[aioredis.ConnectionError],
                            ).client(),
                            prefix=app.settings.redis_prefix,
                        ),
                        cache_ttl=datetime.timedelta(minutes=15),
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

    return decorator


def _serve(app: application.Application[bootstrap.Settings]) -> None:
    starlette.serve(
        factory=_factory(app),
        host=str(app.settings.http_address),
        port=app.settings.http_port,
        allowed_proxy_ips=app.settings.forwarded_allowed_ips,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="plus-webhook")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_serve,
            settings_class=bootstrap.Settings,
        ),
    )
