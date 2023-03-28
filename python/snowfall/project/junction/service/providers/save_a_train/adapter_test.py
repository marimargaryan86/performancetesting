import datetime
from unittest import mock

import pytest_httpx

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.save_a_train import (
    adapter,
    cache,
    conftest,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import phone_number_pb2, postal_address_pb2

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
    responses = conftest.load_json_fixture("booking")
    httpx_mock.add_response(
        method="POST",
        json=responses["selectSearchResult"],
        url="https://test_url/searches/{search_id}/confirm_selection".format(
            search_id=responses["confirmBooking"]["search_identifier"],
        ),
    )
    httpx_mock.add_response(
        method="POST",
        json=responses["makeBooking"],
        url="https://test_url/bookings",
    )
    httpx_mock.add_response(
        method="POST",
        json=responses["confirmBooking"],
        url="https://test_url/bookings/confirm",
    )
    httpx_mock.add_response(
        method="GET",
        json=responses["getTicket"],
        url="https://test_url/order_images/{search_id}".format(
            search_id=responses["confirmBooking"]["search_identifier"],
        ),
    )


async def test_booking_can_be_placed(
    httpx_mock: pytest_httpx.HTTPXMock,
    save_a_train_adapter: adapter.SaveATrainAdapter,
) -> None:
    save_a_train_adapter._notifications_producer.publish = (  # type: ignore[method-assign] # noqa: WPS437, B950
        mock.AsyncMock()
    )

    _mock_responses(httpx_mock)
    booking_proto = await save_a_train_adapter.create_booking(
        task=_ORDER_TASK,
        offer_details=cache.OfferDetails(
            fare_id=1,
            search_id="4Q5lMS",
            search_result_id=2,
            transfer_id=3,
            price="13.37",
            currency="EUR",
        ),
    )
    total_price = money.from_protobuf(booking_proto.total_price)

    assert total_price.currency.code == "EUR"
    assert str(total_price) == "4.50"
    assert booking_proto.trip_result.record_locator == "GTRHSFL"
    assert not booking_proto.trip_result.operator_booking_references
    save_a_train_adapter._notifications_producer.publish.assert_awaited_once()  # noqa: WPS437, B950
