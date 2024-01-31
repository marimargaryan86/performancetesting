import enum
import typing

from snowfall.project.junction.plus.service.notifications.v1 import (
    models_pb2 as notification_models,
)


class PermissionRefs(enum.Enum):
    flight_stats_alerts = "flight_stats_alerts"
    whatsapp_chatbot = "whatsapp_chatbot"


permission_defaults: typing.Sequence[notification_models.Permission] = [
    notification_models.Permission(
        ref=PermissionRefs.flight_stats_alerts.value,
        name="Flight Stats Alerts",
        enabled=False,
    ),
    notification_models.Permission(
        ref=PermissionRefs.whatsapp_chatbot.value,
        name="Whatsapp Chatbot",
        enabled=False,
    ),
]
