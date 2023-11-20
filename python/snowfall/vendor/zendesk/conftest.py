import datetime
from collections.abc import AsyncIterator

import httpx
import pytest

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
