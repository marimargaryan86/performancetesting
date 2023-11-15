from typing import TypeAlias, TypedDict

from snowfall.project.junction.go.service.places.v1 import models_pb2


class ProviderJson(TypedDict):
    id: str
    name: str
    time_zone: str
    latitude: float
    longitude: float


ProviderJsonDict: TypeAlias = dict[str, list[ProviderJson]]
ProviderTypedDict: TypeAlias = dict[
    models_pb2.Location.Type.ValueType,
    ProviderJsonDict,
]
