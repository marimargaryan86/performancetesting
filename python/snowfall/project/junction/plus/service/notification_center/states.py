from collections.abc import Mapping

import prometheus_client

from snowfall.project.junction.plus.notification_channels import (
    channel,
    http_webhook,
    push_notification,
    whatsapp,
)
from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.stdlib.logging import stdout


class Channels(object):
    _notifications_metrics = prometheus_client.Counter(
        "notifications_events_total",
        "Total number of notifications sent through notification center",
        ["sender", "receiver", "channel"],
    )

    def __init__(
        self,
        whatsapp_channel: whatsapp.Channel,
        push_notification_channel: push_notification.Channel,
        http_webhook_channel: http_webhook.Channel,
    ):
        self._channels: Mapping[int, channel.AbstractChannel] = {
            models_pb2.Channel.CHANNEL_WHATSAPP: whatsapp_channel,
            models_pb2.Channel.CHANNEL_PUSH_NOTIFICATION: push_notification_channel,
            models_pb2.Channel.CHANNEL_HTTP_WEBHOOK: http_webhook_channel,
        }
        self._logger = stdout.get_logger()

    async def run(
        self,
        channel_type: int,
        fun: str,
        configuration_vector: models_pb2.ConfigurationVector,
        subscriber: models_pb2.Subscriber,
        event: models_pb2.NotificationEvent,
    ) -> str | None:
        chan = self._get_channel(channel_type)
        if hasattr(chan, fun):  # noqa: WPS421
            self._notifications_metrics.labels(
                sender=configuration_vector.reseller_id,
                receiver=subscriber.id,
                channel=channel_type,
            ).inc()
            return await getattr(chan, fun)(
                sender_configuration=configuration_vector,
                receiver=subscriber,
                event=event,
            )
        raise NotImplementedError(
            "Method: {0} not implemented for channel {1}".format(
                fun,
                chan,
            ),
        )

    def _get_channel(self, channel_type: int) -> channel.AbstractChannel:
        try:
            return self._channels[channel_type]
        except KeyError:
            raise NotImplementedError(
                "Notification channel: {0} is not implemented yet".format(channel_type),
            ) from None
