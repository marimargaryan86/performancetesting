import types

from snowfall.project.junction.go.service.orders.v1alpha import (
    models_pb2 as orders_models,
)
from snowfall.stdlib.v1alpha import models_pb2

_CABIN_MAPPING = types.MappingProxyType(
    {
        "economy": models_pb2.CabinClass.TYPE_ECONOMY,
        "premium_economy": models_pb2.CabinClass.TYPE_PREMIUM,
        "business": models_pb2.CabinClass.TYPE_BUSINESS,
        "first": models_pb2.CabinClass.TYPE_FIRST,
    },
)


def cabin_to_proto(cabin: str | None) -> models_pb2.CabinClass.Type.ValueType:
    if cabin is None:
        return models_pb2.CabinClass.TYPE_UNSPECIFIED

    try:
        return _CABIN_MAPPING[cabin]
    except KeyError:
        return models_pb2.CabinClass.TYPE_UNSPECIFIED


def gender_from_proto(gender: orders_models.Passenger.Gender.ValueType) -> str:
    if gender == orders_models.Passenger.GENDER_MALE:
        return "m"
    elif gender == orders_models.Passenger.GENDER_FEMALE:
        return "f"

    return "u"
