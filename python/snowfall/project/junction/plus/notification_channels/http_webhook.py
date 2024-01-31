import base64
import hashlib
import hmac
from collections.abc import Sequence

import httpx

from snowfall.project.junction.plus.notification_channels.channel import AbstractChannel
from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.stdlib import string


class Channel(AbstractChannel):
    """HTTP Webhook Channel Interface."""

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
        raise NotImplementedError()

    async def preformatted_message(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        return [self.send_message(receiver, sender_configuration, None)]

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
    def __init__(self) -> None:
        self._client = httpx.AsyncClient()
        self._client.headers.update(
            httpx.Headers(
                {
                    "Content-Type": "application/vnd.api+json",
                },
            ),
        )

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
        raise NotImplementedError()

    async def preformatted_message(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        response = await self.send_webhook_message(
            receiver,
            event.preformatted_message,
        )
        return [response]

    async def send_webhook_message(
        self,
        receiver: models_pb2.Subscriber,
        body: str,
    ) -> str:
        signature = hmac.new(
            receiver.webhook_endpoint.encryption_key.encode(),
            body.encode(),
            hashlib.sha512,
        )
        signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
        response = await self._client.request(
            method="POST",
            url=receiver.webhook_endpoint.path,
            json=body,
            headers={"x-junction-signature": signature_b64},
        )
        response.raise_for_status()
        return string.uuid()
