import datetime
from collections.abc import AsyncIterator
from typing import Any
from unittest import mock

import httpx
import pytest
from motor import core

from snowfall.project.junction.go.adapter import passenger_name_records
from snowfall.project.junction.go.service.orders import orders
from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.junction.go.service.resellers.v1 import (
    resellers_pb2,
    resellers_pb2_grpc,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf


@pytest.fixture()
def pnr_client() -> passenger_name_records.Client:
    return passenger_name_records.DictClient([])


@pytest.fixture()
def resellers_client() -> Any:
    stub = mock.create_autospec(resellers_pb2_grpc.ResellerServiceStub, instance=True)
    stub.GetReseller = mock.AsyncMock(return_value=resellers_pb2.GetResellerResponse())

    return stub


@pytest.fixture()
async def journey_repository(
    mongo_client: core.AgnosticClient,
    pnr_client: passenger_name_records.Client,
    resellers_client: Any,
) -> orders.JourneyRepository:
    return orders.JourneyRepository(
        collection=mongo_client.test.journeys,
        passenger_name_records=pnr_client,
        resellers_client=resellers_client,
    )


@pytest.fixture()
async def order_repository(
    mongo_client: core.AgnosticClient,
) -> orders.OrderRepository:
    return orders.OrderRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
async def booking_repository(
    mongo_client: core.AgnosticClient,
) -> orders.BookingRepository:
    return orders.BookingRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
async def booking_details_repository(
    mongo_client: core.AgnosticClient,
) -> orders.BookingDetailsRepository:
    return orders.BookingDetailsRepository(
        collection=mongo_client.test.journeys,
    )


@pytest.fixture()
async def cancellation_requests_repository(
    mongo_client: core.AgnosticClient,
) -> orders.CancellationRequestsRepository:
    return orders.CancellationRequestsRepository(
        collection=mongo_client.test.order_cancellations,
    )


@pytest.fixture()
async def booking_cancellations_repository(
    mongo_client: core.AgnosticClient,
) -> orders.BookingCancellationsRepository:
    return orders.BookingCancellationsRepository(
        collection=mongo_client.test.order_cancellations,
    )


@pytest.fixture()
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


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


@pytest.fixture()
async def cancellation_request(
    cancellation_requests_repository: orders.CancellationRequestsRepository,
    order: models_pb2.Order,
) -> models_pb2.CancellationRequest:
    ticket_ids = iter(["12345", "56789"])
    return await cancellation_requests_repository.insert(
        models_pb2.CancellationRequest(
            booking_cancellations=[
                models_pb2.BookingCancellation(
                    id=string.uuid(),
                    booking_id=booking.id,
                    ticket_id=next(ticket_ids),
                    status=models_pb2.BookingCancellation.STATUS_PENDING,
                )
                for booking in order.bookings
            ],
            status=models_pb2.CancellationRequest.STATUS_PENDING,
            reseller_id="foo",
        ),
    )
