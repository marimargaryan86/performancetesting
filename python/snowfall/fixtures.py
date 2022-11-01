import dataclasses
import datetime
import random
import types
from typing import Sequence

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.orders.v1alpha import (
    models_pb2 as order_models_pb2,
)
from snowfall.project.junction.service.passenger_name_records.v1alpha import (
    passenger_name_records_pb2,
)
from snowfall.project.junction.service.places.v1alpha import (
    models_pb2 as place_models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import (
    latlng_pb2,
    models_pb2,
    phone_number_pb2,
    postal_address_pb2,
)

LATITUDE_RANGE = (-90, 90)
LONGITUDE_RANGE = (-180, 180)

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
LOCATIONS = (
    "e719b289-982c-42f0-99a2-63fa70f8f8c0",
    "c36649e6-71f1-4dfa-aa5a-01c0ede6e538",
)
PLACES = (
    "28a2ee10-d0a7-4a70-89f3-6d587f4dba70",
    "f87c4a6d-fa48-4abb-927c-25447827f5a6",
)
TRIPS = ("9d672f0e-0934-4388-8568-03e40c0bf0e9",)
SCHEDULES = ("d77e4acb-5aa1-47ad-9a15-126c0fa0e157",)
PROVIDER_OFFERS = (
    "88a8dcc9-deff-4a0e-bd96-b0faea5ea90f",
    "fcad7bb3-f74d-4624-a291-eab2cc6ef9ba",
    "b8fabc76-5514-4d95-9af8-740f2cc3a969",
    "91cf7f38-2418-4421-b2f8-87b2d585f6a0",
)
OFFER_SEARCHES = ("cb2c2359-5520-42fc-9bf9-dc78d708cd5e",)
OFFERS = (
    "5927b3ce-fbd7-4f8b-b456-b1b7fd44cdad",
    "c9fb49fc-7f2d-4403-a8b1-5a8c065ea8ce",
)
OFFER_DETAILS = (
    "91d4b3f7-bb9d-4ffc-9919-7892fc017740",
    "c5fabbfa-8e4a-408b-b0d4-8397f103b6b5",
    "14445cd0-1c56-49b6-93fc-e6c7545ad8cf",
    "f3f74630-52e0-4a87-8440-6804f6554f9c",
)
OFFER_GROUPS = (
    "2d178001-46ea-415f-8ec7-f22f2318b7c0",
    "6b368a44-0e01-43cf-80ab-f9a16f40f2b6",
)
OFFER_GROUP_DETAILS = (
    "328bc5eb-3ad0-401a-a765-3335595f2bc7",
    "de20a83e-d2a4-479a-b7b2-27e042da8b2b",
)
SEGMENTS = (
    "9aeed7e9-fa69-4fd5-8590-e14e402e1346",
    "539d336c-a221-4f59-87cb-e4cc305d0cfe",
)
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
JOURNEYS = (
    "586399bc-0d13-4d00-89a1-57f7d7045382",
    "2da9619a-5c28-43b0-9fe6-603257ee2077",
)
ORDERS = (
    "e61d5e73-bb7e-408f-861d-2be84218d1c4",
    "d1c4dec6-be70-4823-bb4c-bff6164de1a7",
)
BOOKINGS = (
    "679283e4-673c-4919-9aac-ba23d5abb4c8",
    "f92b5144-6357-4e7b-a11b-70eb2de2eeee",
)
BOOKING_DETAILS = (
    "5a93b5ae-9590-4561-a664-fbaead485e96",
    "d184081a-92bd-4ec8-af9a-1faaa8dfbbeb",
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


def get_locations() -> list[place_models_pb2.Location]:
    return [generate_location(identifier) for identifier in LOCATIONS]


def generate_location(identifier: str) -> place_models_pb2.Location:
    return place_models_pb2.Location(
        id=identifier,
        name="Foobar",
        coordinates=latlng_pb2.LatLng(
            latitude=random.uniform(*LATITUDE_RANGE),  # nosec
            longitude=random.uniform(*LONGITUDE_RANGE),  # nosec
        ),
        country_code="SE",
        time_zone="Europe/Stockholm",
        types=[place_models_pb2.Location.TYPE_UNSPECIFIED],
    )


def get_places() -> list[place_models_pb2.Place]:
    return [generate_place(identifier) for identifier in PLACES]


def generate_place(identifier: str) -> place_models_pb2.Place:
    return place_models_pb2.Place(
        location=generate_location(identifier),
        merged_ids=LOCATIONS,
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
                        price=money.from_string(
                            string_amount="13.37",
                            currency=money.Currency("SEK"),
                        ).protobuf(),
                        brand_name="PLUS SELECT",
                    ),
                    offers_pb2.Offer(
                        id=PROVIDER_OFFERS[1],
                        segment_details=[
                            offers_pb2.OfferSegmentDetails(
                                id=OFFER_DETAILS[1],
                                offer_segment_id=OFFER_GROUP_DETAILS[0],
                                cabin_class=models_pb2.CabinClass(
                                    type=models_pb2.CabinClass.TYPE_BUSINESS,
                                    marketing_name="Business",
                                ),
                            ),
                        ],
                        price=money.from_string(
                            string_amount="13.37",
                            currency=money.Currency("SEK"),
                        ).protobuf(),
                        brand_name="PLUS FLEX",
                    ),
                ],
                segments=[
                    offers_pb2.OfferSegment(
                        id=OFFER_GROUP_DETAILS[0],
                        segment_id=SEGMENTS[0],
                        legs=[
                            offers_pb2.OfferSegmentLeg(
                                id=string.uuid(),
                                origin=generate_point(string.uuid()),
                                destination=generate_point(string.uuid()),
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
                        trip_sequence=1,
                        segment_sequence=1,
                    ),
                ],
                expires_at=protobuf.datetime_to_protobuf(datetime.datetime.now()),
            ),
            offers_pb2.OfferGroup(
                id=OFFER_GROUPS[1],
                offers=[
                    offers_pb2.Offer(
                        id=PROVIDER_OFFERS[2],
                        segment_details=[
                            offers_pb2.OfferSegmentDetails(
                                id=OFFER_DETAILS[2],
                                offer_segment_id=OFFER_GROUP_DETAILS[1],
                                cabin_class=models_pb2.CabinClass(
                                    type=models_pb2.CabinClass.TYPE_ECONOMY,
                                    marketing_name="Economy",
                                ),
                            ),
                        ],
                        price=money.from_string(
                            string_amount="13.37",
                            currency=money.Currency("SEK"),
                        ).protobuf(),
                        brand_name="PLUS SELECT",
                    ),
                    offers_pb2.Offer(
                        id=PROVIDER_OFFERS[3],
                        segment_details=[
                            offers_pb2.OfferSegmentDetails(
                                id=OFFER_DETAILS[3],
                                offer_segment_id=OFFER_GROUP_DETAILS[1],
                                cabin_class=models_pb2.CabinClass(
                                    type=models_pb2.CabinClass.TYPE_BUSINESS,
                                    marketing_name="Business",
                                ),
                            ),
                        ],
                        price=money.from_string(
                            string_amount="13.37",
                            currency=money.Currency("SEK"),
                        ).protobuf(),
                        brand_name="PLUS FLEX",
                    ),
                ],
                segments=[
                    offers_pb2.OfferSegment(
                        id=OFFER_GROUP_DETAILS[1],
                        segment_id=SEGMENTS[1],
                        legs=[
                            offers_pb2.OfferSegmentLeg(
                                id=string.uuid(),
                                origin=generate_point(string.uuid()),
                                destination=generate_point(string.uuid()),
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
                        trip_sequence=1,
                        segment_sequence=1,
                    ),
                ],
                expires_at=protobuf.datetime_to_protobuf(datetime.datetime.now()),
            ),
        ],
    )


def get_journeys() -> list[order_models_pb2.Journey]:
    return [
        generate_journey(journey_id, order_id, booking_id, [details_id])
        for journey_id, order_id, booking_id, details_id in zip(
            JOURNEYS,
            ORDERS,
            BOOKINGS,
            BOOKING_DETAILS,
        )
    ]


def generate_journey(
    journey_id: str,
    order_id: str,
    booking_id: str,
    option_detail_ids: Sequence[str],
) -> order_models_pb2.Journey:
    price = money.from_string(
        string_amount="13.37",
        currency=money.Currency("GBP"),
    ).protobuf()
    return order_models_pb2.Journey(
        id=journey_id,
        orders=[
            order_models_pb2.Order(
                id=order_id,
                journey_id=journey_id,
                passengers=[
                    order_models_pb2.Passenger(
                        first_name="Foo",
                        last_name="Bar",
                        title=order_models_pb2.Passenger.TITLE_MR,
                        gender=order_models_pb2.Passenger.Gender.GENDER_MALE,
                        date_of_birth=models_pb2.Date(
                            year=1987,
                            month=5,
                            day=24,
                        ),
                    ),
                ],
                bookings=[
                    order_models_pb2.Booking(
                        id=booking_id,
                        order_id=order_id,
                        total_price=price,
                        trip_option=order_models_pb2.TripOption(
                            id=string.uuid(),
                            booking_id=booking_id,
                            price=price,
                            details=[
                                order_models_pb2.TripOptionDetails(
                                    id=detail_id,
                                    booking_id=booking_id,
                                    segment=offers_pb2.OfferSegment(
                                        legs=[
                                            offers_pb2.OfferSegmentLeg(
                                                id=string.uuid(),
                                                origin=generate_point(
                                                    string.uuid(),
                                                ),
                                                destination=generate_point(
                                                    string.uuid(),
                                                ),
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
                                            equipment="77",
                                        ),
                                        operator="BA",
                                        vendor="BA",
                                        type=models_pb2.Schedule.TYPE_AIR,
                                    ),
                                    cabin_class=models_pb2.CabinClass(
                                        type=models_pb2.CabinClass.TYPE_ECONOMY,
                                        marketing_name="Economy",
                                    ),
                                )
                                for detail_id in option_detail_ids
                            ],
                        ),
                    ),
                ],
            ),
        ],
        passenger_name_record="FOOBAR",
        contact_details=order_models_pb2.ContactDetails(
            email="example@example.com",
            address=postal_address_pb2.PostalAddress(
                address_lines=["Street 7"],
                region_code="GB",
                postal_code="10000",
                locality="London",
            ),
            phone=phone_number_pb2.PhoneNumber(
                e164_number="+385996666666",
            ),
        ),
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
        origin=generate_point(string.uuid()),
        destination=generate_point(string.uuid()),
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
