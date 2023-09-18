from collections.abc import Sequence

import lagom
import pydantic

from snowfall.project.junction.plus.adapter import (
    configuration_vectors,
    monitoring_rules,
    notification_event_publisher,
    orders,
    subscribers,
)
from snowfall.project.junction.plus.notification_channels import whatsapp
from snowfall.project.junction.plus.service.plus_webhooks import chatbot_handlers
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    flight_stats_app_key: str
    notifications_address: str
    twilio_sid: str
    twilio_token: str
    redis_dsn: Sequence[pydantic.AnyUrl]
    redis_prefix: str
    openai_api_key: str
    openai_org: str
    shortener_key: str
    shortener_url: str
    shortener_domain: str


def create_dependencies(  # noqa: WPS211
    monitoring_rules_client: monitoring_rules.Client,
    subscribers_client: subscribers.Client,
    orders_client: orders.Client,
    notification_event_publisher_client: notification_event_publisher.Client,
    configuration_vectors_client: configuration_vectors.Client,
    message_handler: chatbot_handlers.MessageHandler,
    whatsapp_channel: whatsapp.Channel,
) -> lagom.Container:
    container = lagom.Container()
    container[monitoring_rules.Client] = monitoring_rules_client  # type: ignore[type-abstract]
    container[subscribers.Client] = subscribers_client  # type: ignore[type-abstract]
    container[orders.Client] = orders_client  # type: ignore[type-abstract]
    container[notification_event_publisher.Client] = notification_event_publisher_client  # type: ignore[type-abstract]
    container[configuration_vectors.Client] = configuration_vectors_client  # type: ignore[type-abstract]
    container[chatbot_handlers.MessageHandler] = message_handler
    container[whatsapp.Channel] = whatsapp_channel
    return container
