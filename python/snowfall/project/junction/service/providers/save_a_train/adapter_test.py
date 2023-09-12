import datetime
from unittest import mock

import pytest
import pytest_httpx

from snowfall.project.junction.go.service.orders.v1 import amqp_pb2, models_pb2
from snowfall.project.junction.go.v1.models_pb2 import CabinClass
from snowfall.project.junction.service.providers.save_a_train import (
    adapter,
    cache,
    conftest,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import phone_number_pb2, postal_address_pb2
from snowfall.vendor.save_a_train import client, enums
from snowfall.vendor.save_a_train.models import request

_BASE_SEARCH_URL = "https://test_url/searches"
_ORIGIN = "SAT_NL_AM_GVFLE"
_DESTINATION = "SAT_NL_RO_LCHPY"
_TRIP_TYPE = 1
_PASSENGER_COUNT = 1
_DATE = "2023-07-02"
_EMAIL = "test%40snowfall.com"
_PASSWORD = "secret"

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


async def _mock_responses(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    responses = await conftest.load_json_fixture("booking")
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
    save_a_train_adapter._notifications_producer.publish = (  # type: ignore[method-assign] # noqa: SLF001
        mock.AsyncMock()
    )

    await _mock_responses(httpx_mock)
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
    total_price = money.from_protobuf(booking_proto.provider_total_price)

    assert total_price.currency.code == "EUR"
    assert str(total_price) == "4.50"
    assert booking_proto.trip_result.record_locator == "GTRHSFL"
    assert not booking_proto.trip_result.operator_booking_references
    save_a_train_adapter._notifications_producer.publish.assert_awaited_once()  # noqa: SLF001


async def test_perform_general_search_route_not_allowed(
    httpx_mock: pytest_httpx.HTTPXMock,
    save_a_train_adapter: adapter.SaveATrainAdapter,
) -> None:
    expected_error_message = "{'errors': ['This route is not allowed']}"
    httpx_mock.add_response(
        url="{0}/{1}/{2}?triptype={3}&passengers={4}&ddate={5}&rdate=&email={6}&password={7}".format(
            _BASE_SEARCH_URL,
            _ORIGIN,
            _DESTINATION,
            _TRIP_TYPE,
            _PASSENGER_COUNT,
            _DATE,
            _EMAIL,
            _PASSWORD,
        ),
        json=expected_error_message,
    )

    with pytest.raises(adapter.RouteNotAllowedError) as excinfo:
        await save_a_train_adapter.perform_general_search(
            search_request=request.GeneralSearchResultsRequest(
                origin_id=_ORIGIN,
                destination_id=_DESTINATION,
                trip_type=enums.TripType.one_way,
                number_of_passengers=_PASSENGER_COUNT,
                departure_date=datetime.date(2023, 7, 2),
            ),
        )

    assert str(excinfo.value) == expected_error_message  # noqa: WPS441


async def test_get_cabin_type(
    save_a_train_adapter: adapter.SaveATrainAdapter,
    save_a_train_client: client.SATClient,
) -> None:
    fare_brands = list(adapter._CABIN_MAPPING.keys())  # noqa: SLF001

    for fare_brand in fare_brands:
        assert (
            await save_a_train_adapter._get_cabin_type_value(fare_brand)  # noqa: SLF001
            == adapter._CABIN_MAPPING[fare_brand]  # noqa: SLF001
        )

    with mock.patch.object(
        save_a_train_client.api_client,
        "get_fare_class",
    ) as mock_get_fare_class:
        mock_get_fare_class.return_value = "First Class"
        assert (
            await save_a_train_adapter._get_cabin_type_value(  # noqa: SLF001
                "Some other First Class value",
            )
            == CabinClass.TYPE_FIRST
        )

        mock_get_fare_class.return_value = ""
        assert (
            await save_a_train_adapter._get_cabin_type_value(  # noqa: SLF001
                "brand not found",
            )
            == CabinClass.TYPE_UNSPECIFIED
        )

        mock_get_fare_class.return_value = "Some new class not mapped yet"
        assert (
            await save_a_train_adapter._get_cabin_type_value(  # noqa: SLF001
                "Super Duper Elite Class",
            )
            == CabinClass.TYPE_UNSPECIFIED
        )
