import pathlib

from twilio.rest import Client as twilioClient

from snowfall.project.junction.plus.notification_channels.channel import AbstractChannel
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf


class Channel(AbstractChannel):
    """Whatsapp Channel Interface."""

    async def send_order_confirmation(
        self,
        order: models_pb2.PersistedOrder,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> None:
        raise NotImplementedError()

    async def send_delay_notification(
        self,
        order: models_pb2.PersistedOrder,
        receiver: models_pb2.Subscriber,
    ) -> None:
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

    async def send_order_confirmation(
        self,
        order: models_pb2.PersistedOrder,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> None:
        bookings_message = "\n".join(
            [
                "from {0} to {1} on {2}".format(
                    booking.value.origin,
                    booking.value.destination,
                    protobuf.protobuf_to_datetime(booking.value.departure_at).strftime(
                        "%A %d %b %Y %H:%M",
                    ),
                )
                for booking in order.bookings
            ],
        )

        self.send_message(
            receiver=receiver.phone_number.e164_number,
            sender_number=sender_configuration.mobile_phone.e164_number,
            body=(
                "We are pleased to confirm that your trip: \n"
                + bookings_message
                + "\nis booked! \n"
                + "Booking Reference: "
                + order.booking_reference
            ),
        )

    async def send_delay_notification(
        self,
        order: models_pb2.PersistedOrder,
        receiver: models_pb2.Subscriber,
    ) -> None:
        raise NotImplementedError("Method not implemented for this channel!")

    def send_message(
        self,
        receiver: str,
        sender_number: str,
        body: str | None,
        media_url: str | None = None,
    ) -> None:
        self._client.messages.create(  # type: ignore[no-untyped-call]
            from_="whatsapp:{0}".format(sender_number),
            body=body,
            media_url=media_url,
            to="whatsapp:{0}".format("".join(receiver.split())),
        )


class MockChannel(Channel):
    def __init__(self) -> None:
        self._sent_messages: list[str] = []

    async def send_order_confirmation(
        self,
        order: models_pb2.PersistedOrder,
        receiver: models_pb2.Subscriber,
        sender_configuration: models_pb2.ConfigurationVector,
    ) -> None:
        self._sent_messages.append(
            "order: {0} from {1} to {2}".format(
                order.id,
                sender_configuration.reseller_id,
                receiver.id,
            ),
        )

    async def send_delay_notification(
        self,
        order: models_pb2.PersistedOrder,
        receiver: models_pb2.Subscriber,
    ) -> None:
        self._sent_messages.append(
            "order delay: {0} to {1}".format(
                order.id,
                receiver.id,
            ),
        )
