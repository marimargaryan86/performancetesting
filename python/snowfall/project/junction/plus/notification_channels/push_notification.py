from collections.abc import Sequence

import firebase_admin
from firebase_admin import (
    credentials as firebase_credentials,
)
from firebase_admin import (
    messaging as firebase_messaging,
)

from snowfall.project.junction.plus.notification_channels.channel import AbstractChannel
from snowfall.project.junction.plus.notification_channels.flight_stats_messages import (
    get_message_from_code,
)
from snowfall.project.junction.plus.notification_channels.order_utils import (
    proto_to_format_dt,
)
from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf


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
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
        body: str | None,
        title: str | None = None,
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
        raise NotImplementedError()

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
        raise NotImplementedError()

    def send_message(
        self,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
        body: str | None,
        title: str | None = None,
        media_url: str | None = None,
    ) -> str:
        return string.uuid()


class ProviderChannel(Channel):
    def __init__(
        self,
        credentials: str,
    ):
        firebase_cred = firebase_credentials.Certificate(credentials)
        self.firebase_app = firebase_admin.initialize_app(firebase_cred)

    async def order_confirmation(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        raise NotImplementedError()

    async def flight_stats_alert(  # noqa: WPS231
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        message_ids = []
        booking_value = event.alert.booking.value
        for update in event.alert.updates:
            if update.HasField("date_field"):
                try:
                    message = get_message_from_code(
                        code=protobuf.enum_value_to_slug(
                            models_pb2.UpdatedDateField.Field.DESCRIPTOR,
                            enum_value=update.date_field.field,
                        ),
                        channel_type=sender_configuration.channel,
                    )
                except KeyError:
                    continue
                message_ids.append(
                    self.send_message(
                        receiver=receiver,
                        sender_configuration=sender_configuration,
                        title=message["title"],
                        body=message["body"].format(
                            booking_value.origin.name,
                            booking_value.destination.name,
                            proto_to_format_dt(
                                update.date_field.original_date_local,
                            ),
                            proto_to_format_dt(update.date_field.new_date_local),
                        ),
                    ),
                )
            else:
                try:
                    message = get_message_from_code(
                        code=protobuf.enum_value_to_slug(
                            models_pb2.UpdatedTextField.Field.DESCRIPTOR,
                            enum_value=update.text_field.field,
                        ),
                        channel_type=sender_configuration.channel,
                    )
                except KeyError:
                    continue
                message_ids.append(
                    self.send_message(
                        receiver=receiver,
                        sender_configuration=sender_configuration,
                        title=message["title"],
                        body=message["body"].format(
                            booking_value.origin.name,
                            booking_value.destination.name,
                            update.text_field.original_text,
                            update.text_field.new_text,
                        ),
                    ),
                )
        return message_ids

    async def preformatted_message(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        raise NotImplementedError()

    def send_message(
        self,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
        body: str | None,
        title: str | None = None,
        media_url: str | None = None,
    ) -> str:
        message = firebase_messaging.Message(
            notification=firebase_messaging.Notification(
                title=title,
                body=body,
            ),
            token=receiver.push_notifications_token,
        )
        return firebase_messaging.send(message)
