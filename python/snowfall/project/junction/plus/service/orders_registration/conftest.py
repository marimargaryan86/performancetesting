from collections.abc import AsyncGenerator
from unittest import mock

import pytest

from snowfall.project.junction.plus.adapter import (
    monitoring_rules as monitoring_rules_adapter,
)
from snowfall.project.junction.plus.adapter import (
    orders as orders_adapter,
)
from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.project.junction.plus.service.orders_registration import flight_stats
from snowfall.project.junction.plus.service.orders_registration.importer import (
    OrderImporter,
)
from snowfall.project.junction.plus.service.orders_registration.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.transport.amqp import types
from snowfall.stdlib.transport.amqp.consumer import Consumer
from snowfall.stdlib.transport.amqp.producer import Producer
from snowfall.stdlib.v1 import latlng_pb2, phone_number_pb2

_latitude = 37.9362
_longitude = 23.948


@pytest.fixture()
def consumer() -> mock.AsyncMock:
    mock_consumer = mock.create_autospec(Consumer)
    return mock_consumer.return_value


@pytest.fixture()
def producer() -> mock.AsyncMock:
    mock_producer = mock.create_autospec(Producer)
    return mock_producer.return_value


@pytest.fixture()
def orders_client() -> orders_adapter.Client:
    return orders_adapter.DictClient([])


@pytest.fixture()
def monitoring_rules_client() -> monitoring_rules_adapter.Client:
    return monitoring_rules_adapter.DictClient([])


@pytest.fixture()
def flight_stats_client() -> flight_stats.Client:
    return flight_stats.DictClient()


@pytest.fixture()
async def invalid_message() -> (
    AsyncGenerator[types.Message[amqp_pb2.IncomingOrder], None]
):
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as mock_message:
        message = mock_message.return_value
        message.body = amqp_pb2.IncomingOrder(
            reseller_id="reseller_id",
        )
        message.processed = False
        message.exchange = None
        message.routing_key = None

        yield message


@pytest.fixture()
async def valid_message() -> (
    AsyncGenerator[types.Message[amqp_pb2.IncomingOrder], None]
):
    flight_number = 2512
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as mock_message:
        message = mock_message.return_value
        message.body = amqp_pb2.IncomingOrder(
            reseller_id="reseller_id",
            external_ref_id="external_ref_id",
            booking_reference="booking_reference",
            contact_details=models_pb2.ContactDetails(
                email="dsada@gmail.com",
                address=models_pb2.PostalAddress(
                    address_lines=["Street name 7"],
                    region_code="GB",
                    postal_code="12345",
                    locality="London",
                ),
                phone=phone_number_pb2.PhoneNumber(
                    e164_number="+46708443755",
                ),
            ),
            passengers=[
                models_pb2.Passenger(
                    first_name="John",
                    last_name="Wick",
                    title=models_pb2.Passenger.Title.TITLE_MR,
                    gender=models_pb2.Passenger.Gender.GENDER_MALE,
                ),
            ],
            bookings=[
                models_pb2.Booking(
                    value=models_pb2.AirBooking(
                        id=string.uuid(),
                        origin=models_pb2.Location(
                            name="London",
                            coordinates=latlng_pb2.LatLng(
                                latitude=_latitude,
                                longitude=_longitude,
                            ),
                        ),
                        destination=models_pb2.Location(
                            name="Amsterdam",
                            coordinates=latlng_pb2.LatLng(
                                latitude=_latitude,
                                longitude=_longitude,
                            ),
                        ),
                        route_identifier=models_pb2.RouteIdentifier(
                            carrier="U2",
                            flight_number=flight_number,
                        ),
                        cabin_class="Economy",
                    ),
                ),
            ],
        )
        message.processed = False
        message.exchange = None
        message.routing_key = None

        yield message


@pytest.fixture()
def order_importer(
    consumer: mock.AsyncMock,
    producer: mock.AsyncMock,
    orders_client: orders_adapter.Client,
    monitoring_rules_client: monitoring_rules_adapter.Client,
    flight_stats_client: flight_stats.Client,
) -> OrderImporter:
    return OrderImporter(
        consumer,
        producer,
        orders_client,
        monitoring_rules_client,
        flight_stats_client,
    )
