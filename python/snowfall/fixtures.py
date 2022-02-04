import random

from snowfall.common.v1alpha import models_pb2

_LATITUDE_RANGE = (-90, 90)
_LONGITUDE_RANGE = (-180, 180)

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
PLACES = (
    "f236a92c-4cfa-468e-85ef-431d25dcd925",
    "488a836d-ec22-439b-a9d8-3c4c386a731e",
)


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
