import lagom

from snowfall.project.junction.plus.adapter import (
    configuration_vectors,
    monitoring_rules,
    notification_event_publisher,
    subscribers,
)
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    flight_stats_app_key: str
    notifications_address: str
    twilio_token: str


def create_dependencies(
    monitoring_rules_client: monitoring_rules.Client,
    subscribers_client: subscribers.Client,
    notification_event_publisher_client: notification_event_publisher.Client,
    configuration_vectors_client: configuration_vectors.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[monitoring_rules.Client] = monitoring_rules_client  # type: ignore[type-abstract]
    container[subscribers.Client] = subscribers_client  # type: ignore[type-abstract]
    container[notification_event_publisher.Client] = notification_event_publisher_client  # type: ignore[type-abstract]
    container[configuration_vectors.Client] = configuration_vectors_client  # type: ignore[type-abstract]
    return container
