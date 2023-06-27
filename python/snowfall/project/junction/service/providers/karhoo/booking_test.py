import datetime

import pytest_httpx

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.karhoo import booking, cache, conftest
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import phone_number_pb2, postal_address_pb2

_ORDER_TASK = amqp_pb2.PlaceOrderTask(
    booking=models_pb2.Booking(),
    contact_details=models_pb2.ContactDetails(
        address=postal_address_pb2.PostalAddress(
            region_code="SE",
            address_lines=["Granitvägen 17B"],
            locality="Uppsala",
            postal_code="75242",
        ),
        phone=phone_number_pb2.PhoneNumber(
            e164_number="+46708443755",
        ),
        email="mb@snowfall.se",
    ),
    passengers=[
        models_pb2.Passenger(
            first_name="William",
            last_name="Never",
            title=models_pb2.Passenger.TITLE_MR,
            gender=models_pb2.Passenger.GENDER_MALE,
            date_of_birth=protobuf.date_to_protobuf(datetime.date(1987, 5, 24)),
        ),
    ],
    metadata=amqp_pb2.OrderMetadata(),
)


def _mock_responses(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        json=conftest.load_json_fixture("booking"),
        url="https://test_url/v1/bookings",
    )


async def test_booking_can_be_placed(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_booking_handler: booking.BookingHandler,
) -> None:
    _mock_responses(httpx_mock)

    booking_proto = await karhoo_booking_handler.book(
        task=_ORDER_TASK,
        details=cache.OfferDetails(
            quote_id="abc",
            expires_at=datetime.datetime(2022, 1, 1, 12, 0, tzinfo=datetime.UTC),
            price="3550.00",
            currency=money.Currency("GBP"),
        ),
    )

    total_price = money.from_protobuf(booking_proto.provider_total_price)

    assert total_price.currency.code == "GBP"
    assert str(total_price) == "3550.00"
    assert booking_proto.trip_result.record_locator == "string"
    assert not booking_proto.trip_result.operator_booking_references
