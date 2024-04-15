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
CAR_RENTAL_SEARCH_ID = "c827332f-3460-4e79-8ff7-336787a2c88c"
RAIL_SEARCH_ID = "cca489c9-fac4-4e33-bf53-7b06052f8116"
FERRY_SEARCH_ID = "ceeb0307-be96-4066-9bdc-5f1b464bbb78"
SEARCHES = (CAR_RENTAL_SEARCH_ID, RAIL_SEARCH_ID, FERRY_SEARCH_ID)
PLACES = ("3debfa7c-9884-5409-86c8-33f3e491382e",)
PLACE_IATAS = ("BER",)
NOT_FOUND_PLACE_IATA = "TTT"
PLACE_NAMES = ("Takoma Park",)
NOT_FOUND_PLACE_NAME = "not existing place"
CAR_RENTAL_SEARCH_RESULTS = (
    "48d5d190-1e02-40a7-9483-fce0902d4c58",
    "a97d713f-60cc-46fa-b207-dce1ff8606d2",
)
RAIL_SEARCH_RESULTS = (
    "33795b04-e724-4a3a-8cab-d188f7ac8e1e",
    "b1382de6-9e7c-421e-9b43-f3bc62a91961",
)
FERRY_SEARCH_RESULTS = (
    "71337c8a-3c87-40b7-95e0-57f38baa6546",
    "eb1019b2-e5cc-4a22-a481-67ad7706415a",
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
FAKE_ID = 1234

PLACE_LATITUDE = 52.5170365
PLACE_LONGITUDE = 13.3888599


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
    )

    if search_request:
        match search_request.WhichOneof("search_criterion"):
            case "rail":
                search.rail.CopyFrom(search_request.rail)
            case "ferry":
                search.ferry.CopyFrom(search_request.ferry)
            case "car_rental":
                search.car_rental.CopyFrom(search_request.car_rental)
    elif identifier == RAIL_SEARCH_ID:
        search.rail.CopyFrom(generate_rail_one_way_search_criterion())
    elif identifier == FERRY_SEARCH_ID:
        search.ferry.CopyFrom(generate_ferry_one_way_search_criterion())
    elif identifier == CAR_RENTAL_SEARCH_ID:
        search.car_rental.CopyFrom(generate_car_rental_criterion())

    return search


def generate_car_rental_offer(offer_id: str) -> searches_pb2.Offer:
    return searches_pb2.Offer(
        id=offer_id,
        price=money_pb2.Money(currency_code="EUR"),
        price_breakdown=[],
        car_rental=searches_pb2.CarRentalOffer(conditional_prices=[]),
    )


def generate_rail_offer(offer_id: str) -> searches_pb2.Offer:
    return searches_pb2.Offer(
        id=offer_id,
        price=money_pb2.Money(currency_code="EUR"),
        price_breakdown=[],
        rail=searches_pb2.RailOffer(cabin_class=[]),
    )


def generate_ferry_offer(offer_id: str) -> searches_pb2.Offer:
    return searches_pb2.Offer(
        id=offer_id,
        price=money_pb2.Money(currency_code="EUR"),
        price_breakdown=[],
        ferry=searches_pb2.FerryOffer(),
    )


def generate_car_rental_result_detail(
    result_detail_id: str,
) -> searches_pb2.ResultDetail:
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


def generate_ferry_result_detail(result_detail_id: str) -> searches_pb2.ResultDetail:
    return searches_pb2.ResultDetail(
        id=result_detail_id,
        ferry=searches_pb2.FerryResultDetail(
            origin=generate_point(string.uuid()),
            destination=generate_point(string.uuid()),
            departure_date=protobuf.datetime_to_protobuf_datetime(
                datetime.datetime.now(tz=datetime.UTC),
            ),
            arrival_date=protobuf.datetime_to_protobuf_datetime(
                datetime.datetime.now(tz=datetime.UTC),
            ),
            outbound_segment=True,
            segment_sequence=1,
            duration_in_minutes=60,
            ferry_operator=searches_pb2.FerryOperator(
                id=123,  # noqa: WPS432
                name="ferry-op",
            ),
        ),
    )


def generate_rail_result_detail(result_detail_id: str) -> searches_pb2.ResultDetail:
    return searches_pb2.ResultDetail(
        id=result_detail_id,
        rail=searches_pb2.RailResultDetail(
            origin=generate_point(string.uuid()),
            destination=generate_point(string.uuid()),
            departure_date=protobuf.datetime_to_protobuf_datetime(
                datetime.datetime.now(tz=datetime.UTC),
            ),
            arrival_date=protobuf.datetime_to_protobuf_datetime(
                datetime.datetime.now(tz=datetime.UTC),
            ),
            outbound_segment=True,
            segment_sequence=1,
        ),
    )


def generate_search_results(search_id: str) -> list[searches_pb2.SearchResult]:
    if search_id == CAR_RENTAL_SEARCH_ID:
        return generate_car_rental_search_results(search_id)
    if search_id == FERRY_SEARCH_ID:
        return generate_ferry_search_results(search_id)

    return generate_rail_search_results(search_id)


def generate_car_rental_search_results(
    search_id: str,
) -> list[searches_pb2.SearchResult]:
    return [
        searches_pb2.SearchResult(
            id=search_result,
            search_id=search_id,
            provider_id=PROVIDERS[0],
            expires_at=EXPIRES_AT,
            offers=[generate_car_rental_offer(offer) for offer in OFFERS],
            result_details=[
                generate_car_rental_result_detail(result_detail)
                for result_detail in RESULT_DETAILS
            ],
        )
        for search_result in CAR_RENTAL_SEARCH_RESULTS
    ]


def generate_ferry_search_results(
    search_id: str,
) -> list[searches_pb2.SearchResult]:
    return [
        searches_pb2.SearchResult(
            id=search_result,
            search_id=search_id,
            provider_id=PROVIDERS[0],
            expires_at=EXPIRES_AT,
            offers=[generate_ferry_offer(offer) for offer in OFFERS],
            result_details=[
                generate_ferry_result_detail(result_detail)
                for result_detail in RESULT_DETAILS
            ],
        )
        for search_result in FERRY_SEARCH_RESULTS
    ]


def generate_rail_search_results(
    search_id: str,
) -> list[searches_pb2.SearchResult]:
    return [
        searches_pb2.SearchResult(
            id=search_result,
            search_id=search_id,
            provider_id=PROVIDERS[0],
            expires_at=EXPIRES_AT,
            offers=[generate_rail_offer(offer) for offer in OFFERS],
            result_details=[
                generate_rail_result_detail(result_detail)
                for result_detail in RESULT_DETAILS
            ],
        )
        for search_result in RAIL_SEARCH_RESULTS
    ]


def generate_ferry_one_way_search_criterion() -> searches_pb2.Ferry:
    return searches_pb2.Ferry(
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


def generate_car_rental_criterion() -> searches_pb2.CarRental:
    return searches_pb2.CarRental(
        origin=generate_point(string.uuid()),
        destination=generate_point(string.uuid()),
        pickup_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
        ),
        return_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
        ),
        driver_age=29,  # noqa: WPS432
    )


def generate_point(identifier: str) -> models_pb2.Point:
    return models_pb2.Point(
        ref=identifier,
        name="Point name",
        coordinates=latlng_pb2.LatLng(
            latitude=15,  # noqa: WPS432
            longitude=15,  # noqa: WPS432
        ),
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
            rail={
                "snowfall_provider_id_rail": "urn:bnds:tstatn_id:DEBRL",
            },
            air={
                "d29f7e2e-b6e2-4d59-b33d-289aebbed3c0": PLACE_IATAS[0],
            },
            ferry={},
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
