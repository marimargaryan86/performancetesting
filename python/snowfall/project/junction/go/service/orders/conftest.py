import datetime
from collections.abc import AsyncIterator

import httpx
import pytest
from motor import motor_asyncio

from snowfall.project.junction.go.adapter import passenger_name_records
from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2
from snowfall.project.junction.go.service.orders.zendesk.client import ZendeskClient
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf


@pytest.fixture()
def pnr_client() -> passenger_name_records.Client:
    return passenger_name_records.DictClient([])


@pytest.fixture()
def journey_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
    pnr_client: passenger_name_records.Client,
) -> orders.JourneyRepository:
    return orders.JourneyRepository(
        collection=mongo_client.test.journeys,
        passenger_name_records=pnr_client,
    )


@pytest.fixture()
def order_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.OrderRepository:
    return orders.OrderRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
def booking_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.BookingRepository:
    return orders.BookingRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
def booking_details_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.BookingDetailsRepository:
    return orders.BookingDetailsRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
def bookings_cancellation_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> orders.BookingsCancellationsRepository:
    return orders.BookingsCancellationsRepository(
        collection=mongo_client.test.order_cancellations,
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
async def order(
    journey_repository: orders.JourneyRepository,
    order_repository: orders.OrderRepository,
) -> models_pb2.Order:
    journey = await journey_repository.create(
        contact_details=models_pb2.ContactDetails(),
        reseller_id="",
    )

    return await order_repository.create_from_options(
        journey_id=journey.id,
        passengers=[
            models_pb2.Passenger(),
        ],
        options=[
            models_pb2.TripOption(
                details=[
                    models_pb2.TripOptionDetails(),
                    models_pb2.TripOptionDetails(),
                ],
                price=money.from_string(
                    string_amount="13.37",
                    currency=money.Currency("GBP"),
                ).protobuf(),
            ),
            models_pb2.TripOption(
                details=[
                    models_pb2.TripOptionDetails(),
                ],
                price=money.from_string(
                    string_amount="133.37",
                    currency=money.Currency("GBP"),
                ).protobuf(),
            ),
        ],
        residence_address=None,
    )


@pytest.fixture()
async def booking() -> models_pb2.Booking:
    return models_pb2.Booking(
        id="foo",
        trip_result=models_pb2.TripBooking(provider_booking_reference="bar"),
        updated_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(datetime.UTC),
        ),
    )
