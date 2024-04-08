import datetime

from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    models_pb2 as searches_pb2,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import (
    amqp_pb2,
    date_pb2,
    latlng_pb2,
    money_pb2,
)

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
RESELLER_ID = "3458f6b0-c6b7-48c8-95cd-b8543eb3a1fc"

PROVIDERS = (
    "28a2ee10-d0a7-4a70-89f3-6d587f4dba33",
    "f87c4a6d-fa48-4abb-927c-25447827f511",
)
SEARCHES = ("cb2c2359-5520-42fc-9bf9-dc78d708cd5e",)
SEARCH_RESULTS = (
    "5927b3ce-fbd7-4f8b-b456-b1b7fd44cdad",
    "c9fb49fc-7f2d-4403-a8b1-5a8c065ea8ce",
)
RESULT_DETAILS = (
    "2d178001-46ea-415f-8ec7-f22f2318b7c0",
    "6b368a44-0e01-43cf-80ab-f9a16f40f2b6",
)
OFFERS = (
    "2d178001-46ea-415f-8ec7-f22f2318b7c0",
    "6b368a44-0e01-43cf-80ab-f9a16f40f2b6",
)
EXPIRES_AT = protobuf.datetime_to_protobuf(
    datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1),
)


def get_searches() -> list[searches_pb2.Search]:
    return [generate_search(identifier) for identifier in SEARCHES]


def get_search_results() -> list[searches_pb2.SearchResult]:
    return [generate_search_result(identifier) for identifier in SEARCH_RESULTS]


def generate_search(identifier: str) -> searches_pb2.Search:
    return searches_pb2.Search(
        id=identifier,
        reseller_id=RESELLER_ID,
        expires_at=EXPIRES_AT,
        status=amqp_pb2.Trackable.Status.STATUS_COMPLETED,
        mock=generate_mock_one_way_search_criterion(),
    )


def generate_offer(offer_id: str) -> searches_pb2.Offer:
    return searches_pb2.Offer(
        id=offer_id,
        price=money_pb2.Money(currency_code="EUR"),
        price_breakdown=[],
        car_rental=searches_pb2.CarRentalOffer(conditional_prices=[]),
    )


def generate_result_detail(result_detail_id: str) -> searches_pb2.ResultDetail:
    return searches_pb2.ResultDetail(
        id=result_detail_id,
        car_rental=searches_pb2.CarRentalResultDetail(
            origin=generate_point(string.uuid()),
            destination=generate_point(string.uuid()),
            pickup_at=protobuf.datetime_to_protobuf_datetime(
                datetime.datetime.now(tz=datetime.UTC),
            ),
            return_at=protobuf.datetime_to_protobuf_datetime(
                datetime.datetime.now(tz=datetime.UTC),
            ),
        ),
    )


def generate_search_result(identifier: str) -> searches_pb2.SearchResult:
    return searches_pb2.SearchResult(
        id=identifier,
        search_id=SEARCHES[0],
        provider_id=PROVIDERS[0],
        expires_at=EXPIRES_AT,
        offers=[generate_offer(offer) for offer in OFFERS],
        result_details=[
            generate_result_detail(result_detail) for result_detail in RESULT_DETAILS
        ],
    )


def generate_mock_one_way_search_criterion() -> searches_pb2.Mock:
    return searches_pb2.Mock(
        origin=generate_point(string.uuid()),
        destination=generate_point(string.uuid()),
        departure_date=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
        ),
        passengers=[
            searches_pb2.Passenger(
                date_of_birth=date_pb2.Date(year=1987, month=5, day=24),  # noqa: WPS432
            ),
        ],
    )


def generate_point(identifier: str) -> models_pb2.Point:
    return models_pb2.Point(
        ref=identifier,
        name="Point name",
        coordinates=latlng_pb2.LatLng(),
        time_zone="Europe/Stockholm",
    )
