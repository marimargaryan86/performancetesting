import pathlib
from collections.abc import Sequence
from contextlib import suppress
from gettext import gettext as _

from twilio.rest import Client as twilioClient

from snowfall.project.junction.plus.adapter.flight_delay_predictor import Prediction
from snowfall.project.junction.plus.notification_channels.channel import AbstractChannel
from snowfall.project.junction.plus.notification_channels.flight_stats_messages import (
    get_message_from_code,
)
from snowfall.project.junction.plus.notification_channels.order_utils import (
    compress_flights,
    proto_to_format_dt,
    proto_to_route_identifier,
)
from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types as redis


class Channel(AbstractChannel):
    """Whatsapp Channel Interface."""

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


class ProviderChannel(Channel):
    def __init__(
        self,
        sid: str,
        token: str,
        redis_client: redis.Client[str],
        templates_root_path: pathlib.Path,
    ):
        self._client = twilioClient(sid, token)
        self._redis = redis_client
        self._templates_root_path = templates_root_path

    async def order_confirmation(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
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
                    journey.origin.name,
                    journey.destination.name,
                    protobuf.protobuf_to_datetime(
                        journey.departure_at,
                    ).strftime("%A %d %b %Y %H:%M"),
                )
            )
            counter += 1

        sid = self.send_message(
            receiver=receiver,
            sender_configuration=sender_configuration,
            body=_(
                "Hi {0},".format(receiver.first_name)
                + "\nWe are pleased to confirm that your {0}trip is booked:".format(
                    trip_type,
                )
                + "\n\n*Booking Reference:* {0}".format(event.body.booking_reference)
                + journey_details
                + message_ending
                + "\n\nTo check your *Trip Details*, please tap the button below",
            ),
        )
        session = self._redis.hash_("message_id_order_id")
        await session.put(sid, event.body.id)
        return [sid]

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
                        body=message["body"].format(
                            booking_value.origin.name,
                            booking_value.destination.name,
                            update.text_field.original_text,
                            update.text_field.new_text,
                        ),
                    ),
                )

        self.send_message(
            receiver=receiver,
            sender_configuration=sender_configuration,
            body=_("Please select one of the following options"),
        )
        return message_ids

    async def preformatted_message(
        self,
        event: models_pb2.NotificationEvent,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> Sequence[str]:
        sid = self.send_message(
            receiver=receiver,
            sender_configuration=sender_configuration,
            body=event.preformatted_message,
        )
        return [sid]

    def send_message(
        self,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
        body: str | None,
        title: str | None = None,
        media_url: str | None = None,
    ) -> str:
        response = self._client.messages.create(  # type: ignore[no-untyped-call]
            from_="whatsapp:{0}".format(sender_configuration.mobile_phone.e164_number),
            body=body,
            media_url=media_url,
            to="whatsapp:{0}".format(
                "".join(receiver.phone_number.e164_number.split()),
            ),
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
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
        body: str | None,
        title: str | None = None,
        media_url: str | None = None,
    ) -> str:
        return string.uuid()


def transform_trip_details(
    order: models_pb2.PersistedOrder,
    delays: Sequence[Prediction] | None,
) -> str:
    return _(
        "Here are the details of your upcoming trip:\n"
        + "*Booking Reference:* {0}\n".format(order.booking_reference)
        + "*Duration:* {0}\n".format(
            str(
                protobuf.protobuf_to_datetime(order.bookings[-1].value.arrival_at)
                - protobuf.protobuf_to_datetime(order.bookings[0].value.departure_at),
            ),
        )
        + "*Stops:* {0}\n\n".format(len(order.bookings))
        + "\n".join(
            [
                (
                    "*Departure from:* {0}\n".format(booking.value.origin.name)
                    + "*Departure at:* {0}\n".format(
                        proto_to_format_dt(booking.value.departure_at),
                    )
                    + "*Arrival to:* {0}\n".format(booking.value.destination.name)
                    + "*Arrival at:* {0}\n".format(
                        proto_to_format_dt(booking.value.arrival_at),
                    )
                    + "*Flight Number:* {0}\n".format(
                        proto_to_route_identifier(booking.value.route_identifier),
                    )
                    + calculate_delay_and_layover(order.bookings, idx, delays)
                )
                for idx, booking in enumerate(order.bookings)
            ],
        ),
    )


def calculate_delay_and_layover(
    bookings: Sequence[models_pb2.Booking],
    idx: int,
    delays: Sequence[Prediction] | None,
) -> str:
    message = ""
    if delays:
        with suppress(IndexError):
            delay = int(delays[idx].delay)
            if delay < 0:
                message = "\n*Predicted arrival early* by {0} mins\n".format(
                    -delay,
                )
            else:
                message = "\n*Predicted arrival delay* by {0} mins\n".format(
                    delay,
                )

    if idx < len(bookings) - 1:
        return message + "\nLayover: {0}\n".format(
            protobuf.protobuf_to_datetime(
                bookings[idx + 1].value.departure_at,
            )
            - protobuf.protobuf_to_datetime(
                bookings[idx].value.arrival_at,
            ),
        )
    return message
