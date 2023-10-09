import datetime
import time

from snowfall.project.junction.plus.adapter import errors as errors_adapter
from snowfall.project.junction.plus.adapter import (
    monitoring_rules as monitoring_rules_adapter,
)
from snowfall.project.junction.plus.adapter import (
    notification_event_publisher as notification_event_publisher_adapter,
)
from snowfall.project.junction.plus.adapter import orders as orders_adapter
from snowfall.project.junction.plus.adapter import subscribers as subscribers_adapter
from snowfall.project.junction.plus.notification_channels.order_utils import (
    compress_flights,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout

_CC_MAX_PAIR_SIZE = 2450
_TIME_WINDOW_IN_HOURS = 48


class WeatherReportCronJob(object):
    def __init__(
        self,
        monitoring_rules: monitoring_rules_adapter.Client,
        subscribers: subscribers_adapter.Client,
        orders: orders_adapter.Client,
        publisher_client: notification_event_publisher_adapter.Client,
    ) -> None:
        self._monitoring_rules = monitoring_rules
        self._subscribers = subscribers
        self._orders = orders
        self._publisher_client = publisher_client
        self._logger = stdout.get_logger()

    async def run(self) -> None:  # noqa: WPS231, WPS210, WPS217
        self._logger.info("Started weather reporter as a cron job")
        candidates = await self._monitoring_rules.get_rules_for_upcoming_events(
            sent_flag="sent_weather_report",
        )
        for candidate in candidates:
            weather_report_window = datetime.datetime.now(
                tz=datetime.UTC,
            ) + datetime.timedelta(
                hours=_TIME_WINDOW_IN_HOURS,
            )
            if (  # noqa: WPS337
                protobuf.protobuf_to_datetime(candidate.booking.value.departure_at)
                < weather_report_window
            ):
                weather_report = await self.generate_weather_report(
                    candidate=candidate,
                )
                for subscriber_id in candidate.subscriber_ids:
                    try:
                        subscriber = await self._subscribers.get(  # noqa: WPS220
                            subscriber_id=subscriber_id,
                        )
                    except errors_adapter.NotFoundError:
                        continue  # noqa: WPS220
                    if await self.is_flight_transit(  # noqa: WPS337
                        subscriber_id=subscriber_id,
                        current_booking=candidate.booking,
                    ):
                        continue  # noqa: WPS220
                    notification_event = models_pb2.NotificationEvent(
                        sender_id=subscriber.reseller_id,
                        receiver_id=subscriber_id,
                        preformatted_message=weather_report,
                        event_type=models_pb2.NotificationEvent.TYPE_PREFORMATTED_MESSAGE,
                        channel=models_pb2.Channel.CHANNEL_WHATSAPP,
                    )
                    await self._publisher_client.publish(notification_event)
                await self._monitoring_rules.sent_weather_report(candidate.id)

    async def is_flight_transit(
        self,
        subscriber_id: str,
        current_booking: models_pb2.Booking,
    ) -> bool:
        subscriber_orders = await self._orders.find(subscriber_id)
        for order in subscriber_orders:
            processed_bookings = compress_flights(
                [
                    booking.value
                    for booking in order.bookings
                    if booking.value.DESCRIPTOR.name == "AirBooking"
                    and booking.value.departure_at.seconds > int(time.time())
                ],
            )
            for booking in processed_bookings:
                if (  # noqa: WPS337
                    current_booking.value.destination.name == booking.destination.name
                    and current_booking.value.arrival_at == booking.arrival_at
                ):
                    return False
        return True

    async def generate_weather_report(
        self,
        candidate: models_pb2.MonitoringRule,
    ) -> str:
        weather_report = "Weather report for flight to {0}".format(
            candidate.booking.value.destination.name,
        )
        self._logger.info(weather_report)
        return weather_report
