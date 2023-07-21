import lagom

from snowfall.project.junction.plus.adapter import monitoring_rules
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    flight_stats_app_key: str
    notifications_address: str
    twilio_token: str


def create_dependencies(
    monitoring_rules_client: monitoring_rules.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[monitoring_rules.Client] = monitoring_rules_client  # type: ignore[type-abstract]
    return container
