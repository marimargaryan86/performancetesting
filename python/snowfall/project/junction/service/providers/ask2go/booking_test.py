import datetime

import pytest
import pytest_httpx

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.ask2go import booking, cache, conftest
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import phone_number_pb2, postal_address_pb2

_GET_BOOKING_URL = "https://test_url/api/Booking?id={id}&transactionId={transaction_id}"
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


def _mock_responses(
    httpx_mock: pytest_httpx.HTTPXMock,
    trip: str,
) -> None:
    httpx_mock.add_response(
        method="POST",
        json=conftest.load_json_fixture("{trip}_post_booking".format(trip=trip)),
        url="https://test_url/api/Booking",
    )
    put_response = conftest.load_json_fixture("{trip}_put_booking".format(trip=trip))
    httpx_mock.add_response(
        method="PUT",
        json=put_response,
        url="https://test_url/api/Booking",
    )
    httpx_mock.add_response(
        method="GET",
        json=conftest.load_json_fixture("{trip}_get_booking".format(trip=trip)),
        url=_GET_BOOKING_URL.format(
            id=put_response["id"],
            transaction_id=put_response["transactionId"],
        ),
    )


@pytest.mark.asyncio
async def test_booking_can_be_placed(
    httpx_mock: pytest_httpx.HTTPXMock,
    booking_handler: booking.BookingHandler,
) -> None:
    _mock_responses(httpx_mock, "ARN_LHR_2022-07-26")
    booking_proto = await booking_handler.book(
        task=_ORDER_TASK,
        details=cache.OfferDetails(pricing_id="foo", transaction_id="bar"),
    )
    total_price = money.from_protobuf(booking_proto.total_price)

    assert booking_proto.provider_name == "Ask2Go"
    assert total_price.currency.code == "EUR"
    assert str(total_price) == "188.07"
    assert booking_proto.trip_result.record_locator == "LLBEIS"
    assert booking_proto.trip_result.operator_booking_references == ["JJODCR"]
