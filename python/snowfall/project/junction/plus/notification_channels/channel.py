import abc
from collections.abc import Sequence

from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2


class AbstractChannel(abc.ABC):
    @abc.abstractmethod
    async def order_confirmation(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        """Send notification for order confirmation."""

    @abc.abstractmethod
    async def flight_stats_alert(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        """Send alerts from flight stats."""

    @abc.abstractmethod
    def send_message(
        self,
        receiver: str,
        sender_number: str,
        body: str | None,
        media_url: str | None = None,
    ) -> str:
        """Send message."""
