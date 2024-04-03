import datetime
from gettext import gettext as _

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
from snowfall.project.junction.plus.service.checkin.checkin_urls import (
    get_open_hours_from_iata,
    get_url_from_iata,
)
from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout

_CC_MAX_PAIR_SIZE = 2450


class CheckinCronJob:
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
        candidates = await self._monitoring_rules.get_rules_for_upcoming_events(
            sent_flag="sent_checkin_reminder",
        )
        for candidate in candidates:
            checkin_window = generate_checkin_window_start(
                carrier=candidate.booking.value.route_identifier.carrier,
            )
            if (  # noqa: WPS337
                protobuf.protobuf_to_datetime(candidate.booking.value.departure_at)
                < checkin_window
            ):
                for subscriber_id in candidate.subscriber_ids:
                    try:
                        subscriber = await self._subscribers.get(  # noqa: WPS220
                            subscriber_id=subscriber_id,
                        )
                    except errors_adapter.NotFoundError:
                        continue  # noqa: WPS220
                    checkin_message = generate_checkin_message(
                        carrier=candidate.booking.value.route_identifier.carrier,
                        destination=candidate.booking.value.destination.name,
                    )
                    notification_event = models_pb2.NotificationEvent(
                        sender_id=subscriber.reseller_id,
                        receiver_id=subscriber_id,
                        preformatted_message=checkin_message,
                        event_type=models_pb2.NotificationEvent.TYPE_PREFORMATTED_MESSAGE,
                    )
                    await self._publisher_client.publish(notification_event)
                await self._monitoring_rules.sent_reminder(candidate.id)
        self._logger.info("Ended check-in reminder as a cron job")


def generate_checkin_message(
    carrier: str,
    destination: str,
) -> str:
    try:
        return _(
            "Check-in for your flight to {0} is now available! "
            "Please follow the link here to check-in: {1}",
        ).format(
            destination,
            get_url_from_iata(carrier),
        )
    except KeyError:
        return _(
            "Check-in for your flight to {0} is now available!",
        ).format(destination)


def generate_checkin_window_start(carrier: str) -> datetime.datetime:
    try:
        hours = get_open_hours_from_iata(carrier)
    except KeyError:
        hours = 24
    return datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
        hours=hours,
    )
