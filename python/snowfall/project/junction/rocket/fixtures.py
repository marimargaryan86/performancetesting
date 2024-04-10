import datetime

from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2 as places_pb2,
)
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
PLACES = ("3debfa7c-9884-5409-86c8-33f3e491382e",)
PLACE_IATAS = ("BER",)
NOT_FOUND_PLACE_IATA = "TTT"
PLACE_NAMES = ("Takoma Park",)
NOT_FOUND_PLACE_NAME = "not existing place"
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

PLACE_LATITUDE = 52.5170365
PLACE_LONGITUDE = 13.3888599


def get_searches() -> list[searches_pb2.Search]:
    return [generate_search(identifier) for identifier in SEARCHES]


def get_search_results() -> list[searches_pb2.SearchResult]:
    return [generate_search_result(identifier) for identifier in SEARCH_RESULTS]


def generate_search(
    identifier: str,
    search_request: searches_pb2.Search | None = None,
    status: amqp_pb2.Trackable.Status.ValueType | None = None,
) -> searches_pb2.Search:
    if not status:
        status = amqp_pb2.Trackable.STATUS_COMPLETED

    search = searches_pb2.Search(
        id=identifier,
        reseller_id=RESELLER_ID,
        expires_at=EXPIRES_AT,
        status=status,
        rail=generate_rail_one_way_search_criterion(),
        search_result_ids=list(SEARCH_RESULTS),
    )

    if search_request:
        match search_request.WhichOneof("search_criterion"):
            case "rail":
                search.rail.CopyFrom(search_request.rail)
            case "ferry":
                search.ferry.CopyFrom(search_request.ferry)
            case "car_rental":
                search.car_rental.CopyFrom(search_request.car_rental)

    return search


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


def generate_rail_one_way_search_criterion() -> searches_pb2.Rail:
    return searches_pb2.Rail(
        origin=generate_point(string.uuid()),
        destination=generate_point(string.uuid()),
        departure_after=protobuf.datetime_to_protobuf(
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


def get_place() -> places_pb2.Place:
    return places_pb2.Place(
        id=PLACES[0],
        name="Berlin",
        coordinates=latlng_pb2.LatLng(
            latitude=PLACE_LATITUDE,
            longitude=PLACE_LONGITUDE,
        ),
        time_zone="Europe/Berlin",
        country_code="DE",
        country_name="Germany",
        type=places_pb2.TYPE_CITY,
        search_capabilities=places_pb2.ProviderMappings(
            rail=[
                places_pb2.ProviderPlaceId(
                    snowfall_provider_id="snowfall_provider_id_rail",
                    provider_place_id="urn:bnds:tstatn_id:DEBRL",
                ),
            ],
            air=[
                places_pb2.ProviderPlaceId(
                    snowfall_provider_id="snowfall_provider_id_air",
                    provider_place_id=PLACE_IATAS[0],
                ),
            ],
            ferry=[],
        ),
        city=places_pb2.PlaceIdentifier(
            id="011c01bd-4e4b-5bf0-a999-ba66175c7f56",
            name=PLACE_NAMES[0],
            type=places_pb2.TYPE_CITY,
        ),
        contains=[
            places_pb2.PlaceIdentifier(
                id="00440ea9-a356-5d32-a714-eb61bcee1fdd",
                name="Zeuthen",
                type=places_pb2.TYPE_AIRPORT,
            ),
        ],
    )
