import dataclasses
import datetime
import random
import types
import uuid

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.orders.v1alpha import (
    models_pb2 as order_models_pb2,
)
from snowfall.project.junction.service.passenger_name_records.v1alpha import (
    passenger_name_records_pb2,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2

_LATITUDE_RANGE = (-90, 90)
_LONGITUDE_RANGE = (-180, 180)

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
PLACES = (
    "28a2ee10-d0a7-4a70-89f3-6d587f4dba70",
    "f87c4a6d-fa48-4abb-927c-25447827f5a6",
)
TRIPS = ("9d672f0e-0934-4388-8568-03e40c0bf0e9",)
SCHEDULES = ("d77e4acb-5aa1-47ad-9a15-126c0fa0e157",)
PROVIDER_OFFERS = ("88a8dcc9-deff-4a0e-bd96-b0faea5ea90f",)
OFFER_SEARCHES = ("cb2c2359-5520-42fc-9bf9-dc78d708cd5e",)
OFFERS = ("5927b3ce-fbd7-4f8b-b456-b1b7fd44cdad",)
OFFER_DETAILS = ("91d4b3f7-bb9d-4ffc-9919-7892fc017740",)
OFFER_GROUPS = ("2d178001-46ea-415f-8ec7-f22f2318b7c0",)
OFFER_GROUP_DETAILS = ("328bc5eb-3ad0-401a-a765-3335595f2bc7",)
SEGMENTS = ("9aeed7e9-fa69-4fd5-8590-e14e402e1346",)
STOPS = (
    "e1f85306-35b3-4892-9e21-a6a34c02459c",
    "d105da8e-8943-4055-8df6-adf0947d9b02",
    "776e5292-7314-4fbf-9a3a-ffb9e039430a",
    "099639fb-ef8f-43f5-8200-423e09d356fd",
)
LEGS = (
    "fe8f2db4-0913-4ece-a3fe-2b3ebecc72ff",
    "71d3750c-d5d4-47aa-9680-e575c34a2979",
)
ORDERS = (
    "e61d5e73-bb7e-408f-861d-2be84218d1c4",
    "d1c4dec6-be70-4823-bb4c-bff6164de1a7",
)
PASSENGER_NAME_RECORDS = ("4567H3LG",)
CURRENCIES_CONVERSIONS = types.MappingProxyType(
    {
        ("USD", "EUR"): 0.95,
        ("EUR", "USD"): 1.05,
    },
)
CURRENCIES = ("USD", "EUR")


@dataclasses.dataclass(frozen=True)
class H3LocationTestModel(object):
    id_: str
    longitude: float
    latitude: float


H3_LOCATIONS = [
    H3LocationTestModel(
        latitude=46.287961,
        longitude=11.232652,
        id_="SAT_IT_MA_XZWAD",
    ),
    H3LocationTestModel(
        latitude=49.2556226,
        longitude=6.8588948,
        id_="SAT_DE_VO_XSTMO",
    ),
    H3LocationTestModel(
        latitude=48.861496,
        longitude=2.33368,
        id_="SAT_FR_PA_WXNGQ",
    ),
    H3LocationTestModel(
        latitude=48.103175,
        longitude=-1.672335,
        id_="SAT_FR_RE_VDQTY",
    ),
]


def get_currencies() -> types.MappingProxyType[tuple[str, str], float]:
    return CURRENCIES_CONVERSIONS


def get_places() -> list[models_pb2.Place]:
    return [generate_place(identifier) for identifier in PLACES]


def generate_place(identifier: str) -> models_pb2.Place:
    return models_pb2.Place(
        id=identifier,
        name="Foobar",
        coordinates=models_pb2.Coordinates(
            latitude=random.uniform(*_LATITUDE_RANGE),  # nosec
            longitude=random.uniform(*_LONGITUDE_RANGE),  # nosec
        ),
        country_code="",
        time_zone="Europe/Stockholm",
        types=[models_pb2.Place.TYPE_UNSPECIFIED],
    )


def get_schedules() -> list[models_pb2.Schedule]:
    return [generate_schedule(identifier) for identifier in SCHEDULES]


def generate_schedule(identifier: str) -> models_pb2.Schedule:
    return models_pb2.Schedule(
        id=identifier,
        stops=[generate_stop(stop_id) for stop_id in STOPS],
    )


def get_segments() -> list[models_pb2.SegmentReference]:
    return [generate_segment_reference(identifier) for identifier in SEGMENTS]


def generate_segment_reference(identifier: str) -> models_pb2.SegmentReference:
    return models_pb2.SegmentReference(
        id=identifier,
        leg_ids=[leg.id for leg in get_legs()],
    )


def generate_stop(stop_id: str) -> models_pb2.Stop:
    return models_pb2.Stop(id=stop_id)


def get_trips() -> list[models_pb2.TripReference]:
    return [generate_trip_reference(identifier) for identifier in TRIPS]


def generate_trip_reference(identifier: str) -> models_pb2.TripReference:
    return models_pb2.TripReference(
        id=identifier,
        segments=get_segments(),
    )


def get_offer_searches() -> list[offers_pb2.OfferSearch]:
    return [generate_offer_search(identifier) for identifier in OFFER_SEARCHES]


def generate_offer_search(identifier: str) -> offers_pb2.OfferSearch:
    return offers_pb2.OfferSearch(
        id=identifier,
    )


def get_offers() -> list[offers_pb2.OfferAggregate]:
    return [generate_offer(identifier) for identifier in OFFERS]


def generate_offer(identifier: str) -> offers_pb2.OfferAggregate:
    return offers_pb2.OfferAggregate(
        id=identifier,
        groups=[
            offers_pb2.OfferGroup(
                id=OFFER_GROUPS[0],
                offer_search_id=OFFER_SEARCHES[0],
                offers=[
                    offers_pb2.Offer(
                        id=PROVIDER_OFFERS[0],
                        segment_details=[
                            offers_pb2.OfferSegmentDetails(
                                id=OFFER_DETAILS[0],
                                offer_segment_id=OFFER_GROUP_DETAILS[0],
                                cabin_class=models_pb2.CabinClass(
                                    type=models_pb2.CabinClass.TYPE_ECONOMY,
                                    marketing_name="Economy",
                                ),
                            ),
                        ],
                        price=models_pb2.Price(
                            amount=1337,
                            currency="SEK",
                        ),
                    ),
                ],
                segments=[
                    offers_pb2.OfferSegment(
                        id=OFFER_GROUP_DETAILS[0],
                        segment_id=SEGMENTS[0],
                        legs=[
                            offers_pb2.OfferSegmentLeg(
                                id=str(uuid.uuid4()),
                                origin=generate_point(str(uuid.uuid4())),
                                destination=generate_point(str(uuid.uuid4())),
                                departure_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
                                arrival_at=protobuf.datetime_to_protobuf(
                                    datetime.datetime.now(),
                                ),
                            ),
                        ],
                        vehicle=offers_pb2.Vehicle(
                            number="123",
                            equipment="FOO",
                        ),
                        operator="SK",
                        vendor="LH",
                    ),
                ],
                expires_at=protobuf.datetime_to_protobuf(datetime.datetime.now()),
            ),
        ],
    )


def get_orders() -> list[order_models_pb2.Order]:
    return [generate_order(identifier) for identifier in ORDERS]


def generate_order(identifier: str) -> order_models_pb2.Order:
    return order_models_pb2.Order(
        id=identifier,
        order_results=[
            order_models_pb2.OrderResult(
                offer_id=offer.id,
            )
            for offer in get_offers()[0].groups[0].offers
        ],
    )


def get_passenger_name_records() -> (
    list[passenger_name_records_pb2.PassengerNameRecord]
):
    return [
        generate_passenger_name_record(identifier)
        for identifier in PASSENGER_NAME_RECORDS
    ]


def generate_passenger_name_record(
    identifier: str,
) -> passenger_name_records_pb2.PassengerNameRecord:
    return passenger_name_records_pb2.PassengerNameRecord(id=identifier)


def get_legs() -> list[models_pb2.Leg]:
    return [generate_leg(identifier) for identifier in LEGS]


def generate_leg(identifier: str) -> models_pb2.Leg:
    return models_pb2.Leg(
        id=identifier,
        origin=generate_point(str(uuid.uuid4())),
        destination=generate_point(str(uuid.uuid4())),
        departure_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(),
        ),
        arrival_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(),
        ),
    )


def generate_point(identifier: str) -> models_pb2.Point:
    return models_pb2.Point(
        ref=identifier,
        name="Point name",
        coordinates=models_pb2.Coordinates(),
        time_zone="Europe/Stockholm",
    )
