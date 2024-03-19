from typing import TypeAlias, TypedDict

from snowfall.project.junction.rocket.service.places.v1alpha import models_pb2


class ProviderJson(TypedDict):
    id: str
    name: str
    time_zone: str
    latitude: float
    longitude: float


ProviderJsonDict: TypeAlias = dict[str, list[ProviderJson]]
ProviderTypedDict: TypeAlias = dict[
    models_pb2.Type.ValueType,
    ProviderJsonDict,
]


ProviderMappings: TypeAlias = dict[
    models_pb2.Type.ValueType,
    list[models_pb2.ProviderPlaceId],
]
