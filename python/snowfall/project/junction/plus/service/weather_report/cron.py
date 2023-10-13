import datetime
import time
import types
from collections.abc import Mapping
from gettext import gettext as _
from typing import Any

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
from snowfall.project.junction.plus.service.weather_report import open_weather_map
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout

_CC_MAX_PAIR_SIZE = 2450
_TIME_WINDOW_IN_HOURS = 48
_WEATHER_CONDITION_GROUP_ICONS = types.MappingProxyType(
    {
        "Thunderstorm": "\U0001f329",
        "Drizzle": "\U0001f327",
        "Rain": "\U0001f327",
        "Snow": "\U0001f328",
        "Clear": "\U0001f31e",
        "Clouds": "\U0001f325",
    },
)


class WeatherReportCronJob(object):
    def __init__(  # noqa: WPS211
        self,
        monitoring_rules: monitoring_rules_adapter.Client,
        subscribers: subscribers_adapter.Client,
        orders: orders_adapter.Client,
        publisher_client: notification_event_publisher_adapter.Client,
        open_weather_map_client: open_weather_map.Client,
    ) -> None:
        self._monitoring_rules = monitoring_rules
        self._subscribers = subscribers
        self._orders = orders
        self._publisher_client = publisher_client
        self._open_weather_map_client = open_weather_map_client
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

    async def generate_weather_report(  # noqa: WPS210
        self,
        candidate: models_pb2.MonitoringRule,
    ) -> str:
        departure_date = protobuf.protobuf_to_datetime(
            candidate.booking.value.departure_at,
        )
        weather_report = _(
            "Your trip to {destination} is in 2 days!\nHere's what the weather forecast"
            " looks like for the first three days of your trip:\n\n\U0001f4cd Location:"
            " {destination}\n\n",
        ).format(
            destination=candidate.booking.value.destination.name,
        )
        weather_forecast = await self._open_weather_map_client.get_weather_forecast(
            candidate.booking.value.destination,
        )
        weather_report += format_daily_weather(
            departure_date,
            weather_forecast,
        )
        weather_report += _("Have a great journey! \U0001f31e")
        return weather_report


def format_daily_weather(
    departure_date: datetime.datetime,
    weather_forecast: Mapping[str, Any],
) -> str:
    hourly_weather_forecast = {
        weather["dt_txt"]: weather for weather in weather_forecast["list"]
    }
    daily_weather_report = ""
    for day_delay in range(3):
        weather_day = departure_date + datetime.timedelta(
            days=day_delay,
        )
        daily_weather_report += _(
            "*Day {0}*\n"
            "\U0001f4c5 {1}\n"
            "\U0001f321 High: {2}°C | Low: {3}°C\n"
            "{4} {5}\n\n",
        ).format(
            day_delay + 1,
            weather_day.strftime("%A %d %B"),
            hourly_weather_forecast[
                "{0} 15:00:00".format(weather_day.strftime("%Y-%m-%d"))
            ]["main"]["temp"],
            hourly_weather_forecast[
                "{0} 03:00:00".format(weather_day.strftime("%Y-%m-%d"))
            ]["main"]["temp"],
            _WEATHER_CONDITION_GROUP_ICONS.get(
                hourly_weather_forecast[
                    "{0} 15:00:00".format(weather_day.strftime("%Y-%m-%d"))
                ]["weather"][0]["main"],
                "\U0001f325",
            ),
            hourly_weather_forecast[
                "{0} 15:00:00".format(weather_day.strftime("%Y-%m-%d"))
            ]["weather"][0]["main"],
        )

    return daily_weather_report
