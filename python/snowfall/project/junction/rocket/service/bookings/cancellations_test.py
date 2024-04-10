import datetime
from unittest import mock

import grpc
import pytest

from snowfall.project.junction.go.v1 import models_pb2 as go_models_pb2
from snowfall.project.junction.rocket.provider.v1alpha import (
    bookings_pb2 as provider_bookings_pb2,
)
from snowfall.project.junction.rocket.service.bookings import cancellations, repository
from snowfall.project.junction.rocket.service.bookings.v1alpha import models_pb2
from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    bookings_pb2,
    bookings_pb2_grpc,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    models_pb2 as searches_models_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.vendor.zendesk import client

_now = datetime.datetime.now(tz=datetime.UTC)
_booking = models_pb2.Booking(
    id="booking-id",
    reseller_id="reseller-id",
    provider_id="provider-id",
    provider_name="provider-name",
    provider_booking=models_pb2.ProviderBooking(
        record_locator="record-locator",
        operator_booking_references=["operator-booking-reference"],
    ),
    trip_option=models_pb2.TripOption(
        price_quote_id="price-quote-id",
        price=money.Money(amount=100, currency=money.Currency("EUR")).protobuf(),
        details=[
            models_pb2.TripOptionDetails(
                rail=searches_models_pb2.RailResultDetail(
                    origin=go_models_pb2.Point(name="London"),
                    destination=go_models_pb2.Point(name="Paris"),
                    departure_date=protobuf.datetime_to_protobuf_datetime(_now),
                ),
            ),
        ],
    ),
    passengers=[
        models_pb2.Passenger(
            first_name="Jon",
            last_name="Doe",
            title=models_pb2.Passenger.TITLE_MR,
            gender=models_pb2.Passenger.GENDER_MALE,
            date_of_birth=protobuf.date_to_protobuf(_now.today()),
        ),
    ],
    status=models_pb2.Booking.STATUS_CONFIRMED,
)
_cancellation = models_pb2.BookingCancellation(
    id="cancellation-id",
    booking_id="booking-id",
)


@pytest.fixture()
def mock_zendesk_client() -> client.ZendeskClient:
    mock_client = mock.create_autospec(client.ZendeskClient)

    mock_client.create_support_ticket = mock.AsyncMock(return_value=1)

    return mock_client


@pytest.fixture()
def manual_handler(
    mock_zendesk_client: client.ZendeskClient,
) -> cancellations.ManualCancellationHandler:
    return cancellations.ManualCancellationHandler(
        zendesk_client=mock_zendesk_client,
        group_id=1,
    )


async def test_getting_updated_when_provider_succeeds(
    booking_repository: repository.BookingRepository,
    booking_cancellation_repository: repository.BookingCancellationRepository,
    manual_handler: cancellations.ManualCancellationHandler,
) -> None:
    booking = await booking_repository.insert(_booking)
    cancellation = await booking_cancellation_repository.insert(_cancellation)

    refunded_us_proto = money.Money(
        amount=100,
        currency=money.Currency("EUR"),
    ).protobuf()

    gateway_stub = mock.create_autospec(bookings_pb2_grpc.BookingServiceStub)
    gateway_stub.CancelBooking = mock.AsyncMock(
        return_value=bookings_pb2.CancelBookingResponse(
            cancellation=provider_bookings_pb2.BookingCancellation(
                provider_booking_reference="provider-booking-reference",
                status=provider_bookings_pb2.BookingCancellation.STATUS_REFUND_DUE,
                refunded_us=refunded_us_proto,
            ),
        ),
    )

    handler = cancellations.CancellationHandler(
        gateway_stub=gateway_stub,
        bookings=booking_repository,
        cancellations=booking_cancellation_repository,
        manual_handler=manual_handler,
    )

    await handler.cancel_booking(booking.id, cancellation.id)

    updated_booking = await booking_repository.find_by_id(booking.id)
    updated_cancellation = await booking_cancellation_repository.find_by_id(
        cancellation.id,
    )

    assert updated_booking
    assert updated_cancellation
    assert updated_booking.status == models_pb2.Booking.STATUS_CANCELLED
    assert (
        updated_cancellation.status == models_pb2.BookingCancellation.STATUS_REFUND_DUE
    )
    assert updated_cancellation.refunded_us == refunded_us_proto


async def test_ticket_created_when_gateway_unavailable(
    booking_repository: repository.BookingRepository,
    booking_cancellation_repository: repository.BookingCancellationRepository,
    manual_handler: cancellations.ManualCancellationHandler,
) -> None:
    booking = await booking_repository.insert(_booking)
    cancellation = await booking_cancellation_repository.insert(_cancellation)

    gateway_stub = mock.create_autospec(bookings_pb2_grpc.BookingServiceStub)
    gateway_stub.CancelBooking = mock.AsyncMock(
        side_effect=grpc.aio.AioRpcError(
            code=grpc.StatusCode.UNAVAILABLE,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        ),
    )

    handler = cancellations.CancellationHandler(
        gateway_stub=gateway_stub,
        bookings=booking_repository,
        cancellations=booking_cancellation_repository,
        manual_handler=manual_handler,
    )

    await handler.cancel_booking(booking.id, cancellation.id)

    updated_cancellation = await booking_cancellation_repository.find_by_id(
        cancellation.id,
    )

    assert updated_cancellation
    assert updated_cancellation.status == models_pb2.BookingCancellation.STATUS_PENDING
    assert updated_cancellation.ticket_id is not None


async def test_ticket_created_when_provider_fails(
    booking_repository: repository.BookingRepository,
    booking_cancellation_repository: repository.BookingCancellationRepository,
    manual_handler: cancellations.ManualCancellationHandler,
) -> None:
    booking = await booking_repository.insert(_booking)
    cancellation = await booking_cancellation_repository.insert(_cancellation)

    gateway_stub = mock.create_autospec(bookings_pb2_grpc.BookingServiceStub)
    gateway_stub.CancelBooking = mock.AsyncMock(
        return_value=bookings_pb2.CancelBookingResponse(
            cancellation=provider_bookings_pb2.BookingCancellation(
                provider_booking_reference="provider-booking-reference",
                status=provider_bookings_pb2.BookingCancellation.STATUS_CANCELLATION_FAILED,
            ),
        ),
    )

    handler = cancellations.CancellationHandler(
        gateway_stub=gateway_stub,
        bookings=booking_repository,
        cancellations=booking_cancellation_repository,
        manual_handler=manual_handler,
    )

    await handler.cancel_booking(booking.id, cancellation.id)

    updated_cancellation = await booking_cancellation_repository.find_by_id(
        cancellation.id,
    )

    assert updated_cancellation
    assert updated_cancellation.status == models_pb2.BookingCancellation.STATUS_PENDING
    assert updated_cancellation.ticket_id is not None
