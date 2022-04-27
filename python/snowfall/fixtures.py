import datetime
import random

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.junction.orders.v1alpha import models_pb2 as order_models_pb2
from snowfall.junction.passenger_name_records.v1alpha import passenger_name_records_pb2
from snowfall.stdlib.format import protobuf

_LATITUDE_RANGE = (-90, 90)
_LONGITUDE_RANGE = (-180, 180)

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
PLACES = (
    "28a2ee10-d0a7-4a70-89f3-6d587f4dba70",
    "f87c4a6d-fa48-4abb-927c-25447827f5a6",
)
TRIPS = ("9d672f0e-0934-4388-8568-03e40c0bf0e9",)
SCHEDULES = ("d77e4acb-5aa1-47ad-9a15-126c0fa0e157",)
OFFERS = ("5927b3ce-fbd7-4f8b-b456-b1b7fd44cdad",)
SEGMENTS = ("9aeed7e9-fa69-4fd5-8590-e14e402e1346",)
STOPS = (
    "e1f85306-35b3-4892-9e21-a6a34c02459c",
    "d105da8e-8943-4055-8df6-adf0947d9b02",
    "776e5292-7314-4fbf-9a3a-ffb9e039430a",
    "099639fb-ef8f-43f5-8200-423e09d356fd",
)
LEGS = ("fe8f2db4-0913-4ece-a3fe-2b3ebecc72ff",)
ORDERS = (
    "e61d5e73-bb7e-408f-861d-2be84218d1c4",
    "d1c4dec6-be70-4823-bb4c-bff6164de1a7",
)
PASSENGER_NAME_RECORDS = ("4567H3LG",)


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
        country_code="SE",
        time_zone="Europe/Stockholm",
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


def get_offers() -> list[offers_pb2.OfferAggregate]:
    return [generate_offer(identifier) for identifier in OFFERS]


def generate_offer(identifier: str) -> offers_pb2.OfferAggregate:
    return offers_pb2.OfferAggregate(
        id=identifier,
        groups=[
            offers_pb2.OfferGroup(
                offers=[
                    offers_pb2.Offer(
                        price=models_pb2.Price(
                            amount=1337,
                            currency="SEK",
                        ),
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
        offers=get_offers()[0].groups[0].offers,
    )


def get_passenger_name_records() -> list[  # noqa: WPS320
    passenger_name_records_pb2.PassengerNameRecord
]:
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
    )
