import datetime

import pytest
import pytest_httpx

from snowfall.project.junction.content.service.duffel import conftest, offers
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import date_pb2
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders import offer_request as request_builder

_ORIGIN = "SYD"
_DESTINATION = "SIN"
_DEPARTURE_AT = datetime.datetime(2023, 2, 23, tzinfo=datetime.UTC)
_ARRIVAL_AT = datetime.datetime(2023, 2, 23, tzinfo=datetime.UTC)
_TYPE = segment_type_pb2.SEGMENT_TYPE_FLIGHT
_TIME_FORMAT = "%H:%M"


@pytest.fixture()
def offers_transformer() -> offers.Transformer:
    return offers.Transformer()


@pytest.fixture()
def offer_searcher(
    duffel_client: client.DuffelClient,
    offers_transformer: offers.Transformer,
) -> offers.Offers:
    return offers.Offers(
        search_client=duffel_client,
        transformer=offers_transformer,
    )


@pytest.fixture()
def offer_search_one_way() -> trips_pb2.SearchOffersRequest:
    return trips_pb2.SearchOffersRequest(
        one_way=trips_pb2.SearchOffersRequest.OneWay(
            trip=trips_pb2.SearchOffersRequest.Trip(
                segments=[
                    trips_pb2.SearchOffersRequest.Segment(
                        origin_ref=_ORIGIN,
                        destination_ref=_DESTINATION,
                        departure_at=protobuf.datetime_to_protobuf_datetime(
                            _DEPARTURE_AT,
                        ),
                        arrival_at=protobuf.datetime_to_protobuf_datetime(_ARRIVAL_AT),
                        type=_TYPE,
                    ),
                ],
            ),
        ),
        passengers=[
            trips_pb2.SearchOffersRequest.Passenger(
                date_of_birth=date_pb2.Date(year=1987, month=5, day=24),
            ),
        ],
    )


@pytest.fixture()
async def offer_search_response(
    httpx_mock: pytest_httpx.HTTPXMock,
    offer_searcher: offers.Offers,
    offer_search_one_way: trips_pb2.SearchOffersRequest,
) -> trips_pb2.SearchOffersResponse:
    httpx_mock.add_response(
        json=await conftest.load_json_fixture(
            "offer_request_response",
            "snowfall.vendor.duffel.client",
        ),
    )

    return await offer_searcher.find_one_way(
        offer_search_one_way.one_way,
        offer_search_one_way.passengers,
    )


class TestOffers(object):
    async def test_one_way_contains_results(
        self,
        offer_search_response: trips_pb2.SearchOffersResponse,
    ) -> None:
        assert len(offer_search_response.offers)


@pytest.fixture()
def offer_result(
    offer_search_response: trips_pb2.SearchOffersResponse,
) -> trips_pb2.Offer:
    return offer_search_response.offers[0]


class TestOfferModel(object):
    async def test_offer_has_id(self, offer_result: trips_pb2.Offer) -> None:
        assert offer_result.id

    async def test_offer_has_expiry(self, offer_result: trips_pb2.Offer) -> None:
        assert offer_result.expires_at.seconds > 0

    async def test_offer_has_price(self, offer_result: trips_pb2.Offer) -> None:
        assert (
            offer_result.price.base_amount.currency_code
        ), "Results should have a base amount"
        assert (
            offer_result.price.tax_amount.currency_code
        ), "Results should have a tax amount"
        assert (
            offer_result.price.total_amount.currency_code
        ), "Results should have a total amount"


@pytest.fixture()
def offer_request(
    offer_search_one_way: trips_pb2.SearchOffersRequest,
) -> request_builder.OfferRequestData:
    return offers.one_way_to_offer_request(
        offer_search_one_way.one_way,
        offer_search_one_way.passengers,
    )


class TestOfferRequest(object):
    def test_passenger_with_age_is_added_to_request(
        self,
        offer_request: request_builder.OfferRequestData,
    ) -> None:
        passengers = offer_request.offer_data.passengers
        assert passengers
        assert passengers[0].age == 35

    def test_slices_are_added_to_request(
        self,
        offer_request: request_builder.OfferRequestData,
    ) -> None:
        slices = offer_request.offer_data.slices
        assert slices

    def test_slice_with_origin_and_destination_is_added_to_request(
        self,
        offer_request: request_builder.OfferRequestData,
    ) -> None:
        first_slice = offer_request.offer_data.slices[0]
        assert first_slice.origin == _ORIGIN
        assert first_slice.destination == _DESTINATION

    def test_slice_with_date_is_added_to_request(
        self,
        offer_request: request_builder.OfferRequestData,
    ) -> None:
        first_slice = offer_request.offer_data.slices[0]
        assert first_slice.departure_date == _DEPARTURE_AT.date()

    def test_slice_with_departure_time_is_added_to_request(
        self,
        offer_request: request_builder.OfferRequestData,
    ) -> None:
        first_slice = offer_request.offer_data.slices[0]
        assert first_slice.departure_time
        departure_time = _DEPARTURE_AT.strftime(_TIME_FORMAT)
        assert first_slice.departure_time.time_from == departure_time
        assert first_slice.departure_time.to == departure_time

    def test_slice_with_arrival_time_is_added_to_request(
        self,
        offer_request: request_builder.OfferRequestData,
    ) -> None:
        first_slice = offer_request.offer_data.slices[0]
        assert first_slice.arrival_time
        arrival_time = _ARRIVAL_AT.strftime(_TIME_FORMAT)
        assert first_slice.arrival_time.time_from == arrival_time
        assert first_slice.arrival_time.to == arrival_time
