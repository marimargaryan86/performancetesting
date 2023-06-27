import abc

from snowfall.project.junction.plus.service.notification_center.v1alpha import (
    models_pb2 as notification_center_models,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2


class AbstractChannel(abc.ABC):
    @abc.abstractmethod
    async def send_order_confirmation(
        self,
        order: models_pb2.PersistedOrder,
        receiver: models_pb2.Subscriber,
        sender_configuration: notification_center_models.ConfigurationVector,
    ) -> None:
        """Send notification for order confirmation."""

    @abc.abstractmethod
    async def send_delay_notification(
        self,
        order: models_pb2.PersistedOrder,
        receiver: models_pb2.Subscriber,
    ) -> None:
        """Send delay notification event."""
