import datetime
from collections.abc import AsyncIterator
from unittest import mock

import httpx
import pytest

from snowfall.project.junction.service.providers.benerail.v1 import (
    amqp_pb2 as br_amqp_pb2,
)
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.zendesk.client import ZendeskClient
from snowfall.vendor.zendesk.models import (
    cancellation_request as cancellation_request_models,
)


@pytest.fixture()
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def zendesk_client(httpx_client: httpx.AsyncClient) -> ZendeskClient:
    return ZendeskClient(
        base_url="https://test.api.com",
        api_key="somefakeapikey123",
        http_client=httpx_client,
        env="local",
    )


@pytest.fixture()
def booking() -> cancellation_request_models.Booking:
    return cancellation_request_models.Booking(
        booking_id="foo",
        price=cancellation_request_models.Price(amount="123", currency="USD"),
        provider_name="Mock",
        trip_reference="foobar",
        operator_booking_references=[
            cancellation_request_models.OperatorBookingReference(
                operator_booking_reference="foo",
            ),
        ],
        trip_options=[
            cancellation_request_models.Segment(
                operator="foo",
                legs=[
                    cancellation_request_models.Leg(
                        origin_name="foo",
                        destination_name="bar",
                        departure_date=str(datetime.datetime.now(datetime.UTC)),
                    ),
                ],
            ),
        ],
    )


@pytest.fixture()
def order() -> cancellation_request_models.Order:
    return cancellation_request_models.Order(
        order_id="foo",
        passengers=[
            cancellation_request_models.Passengers(first_name="foo", last_name="bar"),
        ],
    )


@pytest.fixture()
def journey() -> cancellation_request_models.Journey:
    return cancellation_request_models.Journey(
        reseller_id="foo",
        passenger_name_record="FOOBAR123",
    )


@pytest.fixture()
async def message() -> types.Message[br_amqp_pb2.BookingNotificationTask]:
    with mock.patch("snowfall.stdlib.transport.amqp.types.Message") as mock_message:
        message = mock_message.return_value
        message.body.journey_id = "journey_id"
        message.body.order_id = "order_id"
        message.body.booking_id = "booking_id"
        message.body.br_booking_id = "br_booking_id"
        message.body.br_dnr = "br_dnr"
        message.body.passenger_name_record = "passenger_name_record"
        message.body.departure_at = str(
            datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
        )
        message.body.created_at = datetime.datetime.now(datetime.UTC)

        return message
