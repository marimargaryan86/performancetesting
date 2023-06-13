import types

from snowfall.project.junction.go.service.orders.v1alpha import (
    models_pb2 as orders_models,
)
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.vendor.ba_ndc.models.util import offer_enums, passenger_enums

_CABIN_MAPPING = types.MappingProxyType(
    {
        offer_enums.CabinTypeEnum.economy: models_pb2.CabinClass.TYPE_ECONOMY,
        offer_enums.CabinTypeEnum.premium_economy: models_pb2.CabinClass.TYPE_PREMIUM,
        offer_enums.CabinTypeEnum.business: models_pb2.CabinClass.TYPE_BUSINESS,
        offer_enums.CabinTypeEnum.first: models_pb2.CabinClass.TYPE_FIRST,
    },
)


def cabin_to_proto(
    cabin: offer_enums.CabinTypeEnum | None,
) -> models_pb2.CabinClass.Type.ValueType:
    if cabin is None:
        return models_pb2.CabinClass.TYPE_UNSPECIFIED

    try:
        return _CABIN_MAPPING[cabin]
    except KeyError:
        return models_pb2.CabinClass.TYPE_UNSPECIFIED


def gender_from_proto(
    gender: orders_models.Passenger.Gender.ValueType,
) -> passenger_enums.GenderEnum:
    if gender == orders_models.Passenger.GENDER_MALE:
        return passenger_enums.GenderEnum.male
    if gender == orders_models.Passenger.GENDER_FEMALE:
        return passenger_enums.GenderEnum.female

    return passenger_enums.GenderEnum.unspecified
