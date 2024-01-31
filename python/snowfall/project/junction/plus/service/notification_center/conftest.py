from collections.abc import AsyncGenerator
from unittest import mock

import pytest

from snowfall.project.junction.plus.adapter import (
    configuration_vectors,
    subscribers,
)
from snowfall.project.junction.plus.notification_channels import (
    http_webhook,
    push_notification,
    whatsapp,
)
from snowfall.project.junction.plus.service.notification_center import (
    importer,
    states,
)
from snowfall.project.junction.plus.service.notifications.v1 import (
    models_pb2 as notifications_models_pb2,
)
from snowfall.stdlib.transport.amqp import types
from snowfall.stdlib.transport.amqp.consumer import Consumer
from snowfall.stdlib.v1 import latlng_pb2, phone_number_pb2

_latitude = 37.9362
_longitude = 23.948


@pytest.fixture()
def consumer() -> mock.AsyncMock:
    mock_consumer = mock.create_autospec(Consumer)
    return mock_consumer.return_value


@pytest.fixture()
def configuration_vectors_client() -> configuration_vectors.Client:
    return configuration_vectors.DictClient(
        [
            notifications_models_pb2.ConfigurationVector(
                id="id",
                reseller_id="reseller_id",
                channel=notifications_models_pb2.Channel.CHANNEL_WHATSAPP,
                mobile_phone=phone_number_pb2.PhoneNumber(
                    e164_number="+46708443755",
                ),
                email="example@example.com",
            ),
        ],
    )


@pytest.fixture()
def subscribers_client() -> subscribers.Client:
    return subscribers.DictClient(
        [
            notifications_models_pb2.Subscriber(
                id="subscriber_id",
                reseller_id="reseller_id",
                phone_number=phone_number_pb2.PhoneNumber(
                    e164_number="+46708443755",
                ),
                email="example@example.com",
            ),
        ],
    )


@pytest.fixture()
def whatsapp_channel() -> whatsapp.Channel:
    return whatsapp.MockChannel()


@pytest.fixture()
def push_notification_channel() -> push_notification.Channel:
    return push_notification.MockChannel()


@pytest.fixture()
def http_webhook_channel() -> http_webhook.Channel:
    return http_webhook.MockChannel()


@pytest.fixture()
def channels(
    whatsapp_channel: whatsapp.Channel,
    push_notification_channel: push_notification.Channel,
    http_webhook_channel: http_webhook.Channel,
) -> states.Channels:
    return states.Channels(
        whatsapp_channel=whatsapp_channel,
        push_notification_channel=push_notification_channel,
        http_webhook_channel=http_webhook_channel,
    )


@pytest.fixture()
async def invalid_message() -> (
    AsyncGenerator[types.Message[notifications_models_pb2.NotificationEvent], None]
):
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as mock_message:
        message = mock_message.return_value
        message.body = notifications_models_pb2.NotificationEvent(
            sender_id="sender_id",
        )
        message.processed = False
        message.exchange = None
        message.routing_key = None

        yield message


@pytest.fixture()
async def valid_message() -> (
    AsyncGenerator[types.Message[notifications_models_pb2.NotificationEvent], None]
):
    flight_number = 2512
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as mock_message:
        message = mock_message.return_value
        message.body = notifications_models_pb2.NotificationEvent(
            sender_id="reseller_id",
            receiver_id="subscriber_id",
            body=notifications_models_pb2.PersistedOrder(
                id="id",
                reseller_id="reseller_id",
                external_ref_id="external_ref_id",
                booking_reference="booking_reference",
                subscriber_id="subscriber_id",
                passengers=[
                    notifications_models_pb2.Passenger(
                        first_name="John",
                        last_name="Wick",
                        title=notifications_models_pb2.Passenger.Title.TITLE_MR,
                        gender=notifications_models_pb2.Passenger.Gender.GENDER_MALE,
                    ),
                ],
                bookings=[
                    notifications_models_pb2.Booking(
                        value=notifications_models_pb2.AirBooking(
                            id="id",
                            origin=notifications_models_pb2.Location(
                                name="Zvartnots International Airport",
                                coordinates=latlng_pb2.LatLng(
                                    latitude=_latitude,
                                    longitude=_longitude,
                                ),
                            ),
                            destination=notifications_models_pb2.Location(
                                name="Paris Charles de Gaulle Airport",
                                coordinates=latlng_pb2.LatLng(
                                    latitude=_latitude,
                                    longitude=_longitude,
                                ),
                            ),
                            origin_iata="LND",
                            destination_iata="AMS",
                            route_identifier=notifications_models_pb2.RouteIdentifier(
                                carrier="U2",
                                flight_number=flight_number,
                            ),
                            cabin_class="Economy",
                        ),
                    ),
                ],
            ),
            event_type=notifications_models_pb2.NotificationEvent.TYPE_ORDER_CONFIRMATION,
        )
        message.processed = False
        message.exchange = None
        message.routing_key = None

        yield message


@pytest.fixture()
def notification_event_importer(
    consumer: mock.AsyncMock,
    configuration_vectors_client: configuration_vectors.Client,
    subscribers_client: subscribers.Client,
    channels: states.Channels,
) -> importer.NotificationEventImporter:
    return importer.NotificationEventImporter(
        consumer,
        configuration_vectors_client,
        subscribers_client,
        channels,
    )
