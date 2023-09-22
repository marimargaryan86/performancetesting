import datetime

from snowfall.project.junction.plus.adapter import (
    errors as errors_adapter,
)
from snowfall.project.junction.plus.adapter import (
    monitoring_rules as monitoring_rules_adapter,
)
from snowfall.project.junction.plus.adapter import (
    notification_event_publisher as notification_event_publisher_adapter,
)
from snowfall.project.junction.plus.adapter import subscribers as subscribers_adapter
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout

_CC_MAX_PAIR_SIZE = 2450


class CheckinCronJob(object):
    def __init__(
        self,
        monitoring_rules: monitoring_rules_adapter.Client,
        subscribers: subscribers_adapter.Client,
        publisher_client: notification_event_publisher_adapter.Client,
    ) -> None:
        self._monitoring_rules = monitoring_rules
        self._subscribers = subscribers
        self._publisher_client = publisher_client
        self._logger = stdout.get_logger()

    async def run(self) -> None:  # noqa: WPS231
        self._logger.info("Started check-in reminder as a cron job")
        next_day = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
            hours=24,
        )
        for candidate in await self._monitoring_rules.get_checkin_candidates():
            if (  # noqa: WPS337
                protobuf.protobuf_to_datetime(candidate.booking.value.departure_at)
                < next_day
            ):
                for subscriber_id in candidate.subscriber_ids:
                    try:
                        subscriber = await self._subscribers.get(  # noqa: WPS220
                            subscriber_id=subscriber_id,
                        )
                    except errors_adapter.NotFoundError:
                        continue  # noqa: WPS220
                    notification_event = models_pb2.NotificationEvent(
                        sender_id=subscriber.reseller_id,
                        receiver_id=subscriber_id,
                        preformatted_message="Checkin reminder!",
                        event_type=models_pb2.NotificationEvent.TYPE_PREFORMATTED_MESSAGE,
                        channel=models_pb2.Channel.CHANNEL_WHATSAPP,
                    )
                    await self._publisher_client.publish(notification_event)
                await self._monitoring_rules.sent_reminder(candidate.id)
        self._logger.info("Ended check-in reminder as a cron job")
