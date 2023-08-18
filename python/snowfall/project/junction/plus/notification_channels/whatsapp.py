import pathlib
from collections.abc import Sequence

from twilio.rest import Client as twilioClient

from snowfall.project.junction.plus.adapter import format
from snowfall.project.junction.plus.notification_channels.channel import AbstractChannel
from snowfall.project.junction.plus.notification_channels.order_utils import (
    compress_flights,
    proto_to_format_dt,
    proto_to_route_identifier,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf


class Channel(AbstractChannel):
    """Whatsapp Channel Interface."""

    async def order_confirmation(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> str:
        raise NotImplementedError()

    async def flight_stats_alert(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> str:
        raise NotImplementedError()


class ProviderChannel(Channel):
    def __init__(
        self,
        sid: str,
        token: str,
        templates_root_path: pathlib.Path,
    ):
        self._client = twilioClient(sid, token)
        self._templates_root_path = templates_root_path

    async def order_confirmation(  # noqa: WPS210
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> str:
        trip_type = ""
        counter = 0
        journey_details = ""
        message_ending = ""
        processed_bookings = compress_flights(
            [
                booking.value
                for booking in event.body.bookings
                if booking.value.DESCRIPTOR.name == "AirBooking"
            ],
        )
        if (  # noqa: WPS337
            len(processed_bookings) == 2
            and processed_bookings[0].origin_iata
            == processed_bookings[1].destination_iata
        ):
            trip_type = "round "
        if len(processed_bookings) > 1:
            counter = 1
        for journey in processed_bookings:
            if counter > 2:
                message_ending = "\n\nAnd {0} more Journeys".format(
                    len(processed_bookings) - 2,
                )
                break
            journey_details += (
                "\n\n*Journey{0}:*\n\n*From:* {1}\n*To:* {2}\n*On:* {3}".format(
                    " {0}".format(counter) if counter else "",
                    journey.origin,
                    journey.destination,
                    protobuf.protobuf_to_datetime(
                        journey.departure_at,
                    ).strftime("%A %d %b %Y %H:%M"),
                )
            )
            counter += 1

        return self.send_message(
            receiver=receiver.phone_number.e164_number,
            sender_number=sender_configuration.mobile_phone.e164_number,
            body=(
                "Hi {0},".format(receiver.first_name)
                + "\nWe are pleased to confirm that your {0}trip is booked:".format(
                    trip_type,
                )
                + "\n\n*Booking Reference:* {0}".format(event.body.booking_reference)
                + journey_details
                + message_ending
                + "\n\nTo check your *Trip Details*, please tap the button below"
            ),
        )

    async def flight_stats_alert(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> str:
        return self.send_message(
            receiver=receiver.phone_number.e164_number,
            sender_number=sender_configuration.mobile_phone.e164_number,
            body="Gate number 7 for your flight {0} it's now open".format(
                format.proto_to_route_identifier(
                    event.alert.booking.value.route_identifier,
                ),
            ),
        )

    def send_message(
        self,
        receiver: str,
        sender_number: str,
        body: str | None,
        media_url: str | None = None,
    ) -> str:
        response = self._client.messages.create(  # type: ignore[no-untyped-call]
            from_="whatsapp:{0}".format(sender_number),
            body=body,
            media_url=media_url,
            to="whatsapp:{0}".format("".join(receiver.split())),
        )
        return response.sid


class MockChannel(Channel):
    def __init__(self) -> None:
        self._sent_messages: list[str] = []

    async def order_confirmation(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> str:
        self._sent_messages.append(
            "order: {0} from {1} to {2}".format(
                event.body.id,
                sender_configuration.reseller_id,
                receiver.id,
            ),
        )
        return str(event.body.id)

    async def flight_stats_alert(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> str:
        self._sent_messages.append(
            "flight stats alert: {0} to {1}".format(
                event.alert.monitoring_rule_id,
                receiver.id,
            ),
        )
        return str(event.body.id)


def transform_trip_details(order: models_pb2.PersistedOrder) -> str:
    return (
        "Here are the details of your upcoming trip:\n"
        + "Booking Reference: {0}\n".format(order.booking_reference)
        + "Duration: {0}\n".format(
            str(
                protobuf.protobuf_to_datetime(order.bookings[-1].value.arrival_at)
                - protobuf.protobuf_to_datetime(order.bookings[0].value.departure_at),
            ),
        )
        + "Stops: {0}\n\n".format(len(order.bookings))
        + "\n".join(
            [
                (
                    "Departure from: {0}\n".format(booking.value.origin)
                    + "Departure at: {0}\n".format(
                        proto_to_format_dt(booking.value.departure_at),
                    )
                    + "Arrival to: {0}\n".format(booking.value.destination)
                    + "Arrival at: {0}\n".format(
                        proto_to_format_dt(booking.value.arrival_at),
                    )
                    + "Flight Number: {0}\n".format(
                        proto_to_route_identifier(booking.value.route_identifier),
                    )
                    + calculate_layover(order.bookings, idx)
                )
                for idx, booking in enumerate(order.bookings)
            ],
        )
    )


def calculate_layover(bookings: Sequence[models_pb2.Booking], idx: int) -> str:
    if idx < len(bookings) - 1:
        return "\nLayover: {0}\n".format(
            protobuf.protobuf_to_datetime(
                bookings[idx + 1].value.departure_at,
            )
            - protobuf.protobuf_to_datetime(
                bookings[idx].value.arrival_at,
            ),
        )
    return ""
