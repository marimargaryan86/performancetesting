from collections.abc import Sequence

from snowfall.project.junction.plus.notification_channels.channel import AbstractChannel
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib import string


class Channel(AbstractChannel):
    """In-app Channel Interface."""

    async def order_confirmation(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        raise NotImplementedError()

    async def flight_stats_alert(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        raise NotImplementedError()

    async def preformatted_message(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        raise NotImplementedError()

    def send_message(
        self,
        receiver: str,
        sender_number: str,
        body: str | None,
        media_url: str | None = None,
    ) -> str:
        raise NotImplementedError()


class MockChannel(Channel):
    def __init__(self) -> None:
        self._sent_messages: list[str] = []

    async def order_confirmation(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        self._sent_messages.append(
            "order: {0} from {1} to {2}".format(
                event.body.id,
                sender_configuration.reseller_id,
                receiver.id,
            ),
        )
        return [str(event.body.id)]

    async def flight_stats_alert(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        self._sent_messages.append(
            "flight stats alert: {0} to {1}".format(
                event.alert.monitoring_rule_id,
                receiver.id,
            ),
        )
        return [str(event.alert.monitoring_rule_id)]

    async def preformatted_message(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        self._sent_messages.append(
            event.preformatted_message,
        )
        return [str(event.receiver_id)]

    def send_message(
        self,
        receiver: str,
        sender_number: str,
        body: str | None,
        media_url: str | None = None,
    ) -> str:
        return string.uuid()


class ProviderChannel(Channel):
    async def order_confirmation(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        return ["Handle in-app order confirmation message."]

    async def flight_stats_alert(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        return ["Handle in-app flight stats alert message."]

    async def preformatted_message(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        return ["Handle in-app preformatted message."]

    def send_message(
        self,
        receiver: str,
        sender_number: str,
        body: str | None,
        media_url: str | None = None,
    ) -> str:
        return "Send in-app message."
