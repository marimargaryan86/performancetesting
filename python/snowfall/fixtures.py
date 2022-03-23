import random

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.orders.v1alpha import orders_pb2

_LATITUDE_RANGE = (-90, 90)
_LONGITUDE_RANGE = (-180, 180)

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
PLACES = (
    "f236a92c-4cfa-468e-85ef-431d25dcd925",
    "488a836d-ec22-439b-a9d8-3c4c386a731e",
)
TRIP = "b3e45af0-f3ae-46e5-a94f-fd1c9d86fb7d"
TRIPS = ("b3e45af0-f3ae-46e5-a94f-fd1c9d86fb7d",)
SCHEDULES = ("as3bs02s-bask-awe4-sye2-sanpl5j1093h",)
OFFERS = ("567890u7-asdf-asdf-7yhs-bn23eiuy083g",)
SEGMENTS = ("f236a92c-4cfa-468e-85ef-431d25dcd925",)
ORDERS = ("f236a92c-4cfa-468e-85ef-431d25dcd925",)


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
    )


def get_segments() -> list[models_pb2.SegmentReference]:
    return [generate_segment_reference(identifier) for identifier in SEGMENTS]


def generate_segment_reference(identifier: str) -> models_pb2.SegmentReference:
    return models_pb2.SegmentReference(
        id=identifier,
    )


def get_trips() -> list[models_pb2.TripReference]:
    return [generate_trip_reference(identifier) for identifier in TRIPS]


def generate_trip_reference(identifier: str) -> models_pb2.TripReference:
    return models_pb2.TripReference(
        id=identifier,
    )


def get_offers() -> list[offers_pb2.OfferAggregate]:
    return [generate_offer_reference(identifier) for identifier in OFFERS]


def generate_offer_reference(identifier: str) -> offers_pb2.OfferAggregate:
    return offers_pb2.OfferAggregate(
        id=identifier,
    )


def get_orders() -> list[orders_pb2.Order]:
    return [generate_order(identifier) for identifier in ORDERS]


def generate_order(identifier: str) -> orders_pb2.Order:
    return orders_pb2.Order(
        id=identifier,
    )
