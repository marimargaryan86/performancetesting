import abc
import collections
import datetime
import functools
from enum import IntEnum
from typing import Any, Mapping, Type

import pydantic
from dateutil import parser
from google.protobuf import descriptor, timestamp_pb2

from snowfall.stdlib.v1alpha import latlng_pb2, models_pb2

_Metadata = descriptor.Descriptor | Type[pydantic.BaseModel]
_TypesMap = Mapping[str, Mapping[str, str]]

_MONGO_ID_KEY = "_id"
_MODEL_ID_KEY = "id"
_LAT_KEY = "latitude"
_LON_KEY = "longitude"
_COORDINATES_KEY = "coordinates"


class Normalizer(abc.ABC):
    @abc.abstractmethod
    def normalize(self, maybe_dict: Any) -> Any:
        """"""

    @abc.abstractmethod
    def denormalize(self, maybe_dict: Any) -> Any:
        """"""

    @abc.abstractmethod
    def supports(self, fqn: str) -> bool:
        """"""


class _CoordinatesNormalizer(Normalizer):
    def denormalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        return {
            _LAT_KEY: maybe_dict[_COORDINATES_KEY][1],
            _LON_KEY: maybe_dict[_COORDINATES_KEY][0],
        }

    def supports(self, fqn: str) -> bool:
        return fqn == models_pb2.Coordinates().DESCRIPTOR.full_name

    def normalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        return {
            "type": "Point",
            _COORDINATES_KEY: [
                maybe_dict[_LON_KEY],
                maybe_dict[_LAT_KEY],
            ],
        }


class _IdNormalizer(Normalizer):
    def denormalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        if isinstance(maybe_dict, dict) and _MONGO_ID_KEY in maybe_dict:
            maybe_dict[_MODEL_ID_KEY] = maybe_dict.pop(_MONGO_ID_KEY)

        return maybe_dict

    def supports(self, fqn: str) -> bool:
        return True

    def normalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        if isinstance(maybe_dict, dict) and _MODEL_ID_KEY in maybe_dict:
            maybe_dict[_MONGO_ID_KEY] = maybe_dict.pop(_MODEL_ID_KEY)

        return maybe_dict


class _LatLngNormalizer(Normalizer):
    def denormalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        return {
            _LAT_KEY: maybe_dict[_COORDINATES_KEY][1],
            _LON_KEY: maybe_dict[_COORDINATES_KEY][0],
        }

    def supports(self, fqn: str) -> bool:
        return fqn == latlng_pb2.LatLng().DESCRIPTOR.full_name

    def normalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        return {
            "type": "Point",
            _COORDINATES_KEY: [
                maybe_dict[_LON_KEY],
                maybe_dict[_LAT_KEY],
            ],
        }


class _TimestampNormalizer(Normalizer):
    def denormalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        if not maybe_dict.tzinfo:
            maybe_dict = maybe_dict.replace(tzinfo=datetime.timezone.utc)

        return maybe_dict.isoformat()

    def supports(self, fqn: str) -> bool:
        return fqn == timestamp_pb2.Timestamp().DESCRIPTOR.full_name

    def normalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        return parser.isoparse(maybe_dict)


class _NormalizerMode(IntEnum):
    normalize = 1
    denormalize = 2


_additional: list[Normalizer] = []
_normalizers: list[Normalizer] = [
    _CoordinatesNormalizer(),
    _IdNormalizer(),
    _LatLngNormalizer(),
    _TimestampNormalizer(),
]


def register(normalizer: Normalizer) -> None:
    if isinstance(normalizer, tuple(type(registered) for registered in _additional)):
        return

    _additional.append(normalizer)


def normalize(metadata: _Metadata, maybe_dict: Any) -> Any:
    return _transform(
        _metadata_fqn(metadata),
        _metadata_to_types_map(metadata),
        maybe_dict,
        _NormalizerMode.normalize,
    )


def denormalize(metadata: _Metadata, maybe_dict: Any) -> Any:
    return _transform(
        _metadata_fqn(metadata),
        _metadata_to_types_map(metadata),
        maybe_dict,
        _NormalizerMode.denormalize,
    )


def _apply_normalizers(fqn: str, mode: _NormalizerMode, maybe_dict: Any) -> Any:
    match mode:
        case _NormalizerMode.normalize:
            normalizers = [*_additional, *_normalizers]
        case _NormalizerMode.denormalize:
            normalizers = [*_normalizers, *_additional]

    for normalizer in normalizers:
        if not normalizer.supports(fqn):
            continue

        match mode:
            case _NormalizerMode.normalize:
                maybe_dict = normalizer.normalize(maybe_dict)
            case _NormalizerMode.denormalize:
                maybe_dict = normalizer.denormalize(maybe_dict)

    return maybe_dict


def _transform(
    fqn: str,
    types_map: _TypesMap,
    maybe_dict: Any,
    mode: _NormalizerMode,
) -> Any:
    maybe_dict = _apply_normalizers(fqn, mode, maybe_dict)

    if not isinstance(maybe_dict, dict):
        return maybe_dict

    for key, dict_value in maybe_dict.items():
        if key not in types_map[fqn]:
            continue

        if isinstance(dict_value, list):
            for idx, list_value in enumerate(dict_value):
                maybe_dict[key][idx] = _transform(
                    types_map[fqn][key],
                    types_map,
                    list_value,
                    mode,
                )
        else:
            maybe_dict[key] = _transform(
                types_map[fqn][key],
                types_map,
                dict_value,
                mode,
            )

    return maybe_dict


def _class_fqn(type_: Type[object]) -> str:
    return ".".join([type_.__module__, type_.__name__])


def _metadata_fqn(metadata: _Metadata) -> str:
    if isinstance(metadata, descriptor.Descriptor):
        return metadata.full_name

    return _class_fqn(metadata)


@functools.cache
def _protobuf_to_types_map(model: descriptor.Descriptor) -> _TypesMap:
    queue = collections.deque([model])
    types_map: dict[str, dict[str, str]] = {}

    while len(queue):
        model = queue.popleft()

        if model.full_name in types_map:
            continue

        types_map[model.full_name] = {}

        for field in model.fields:
            if field.message_type:
                types_map[model.full_name][field.name] = field.message_type.full_name
                queue.append(field.message_type)

    return types_map


@functools.cache
def _pydantic_to_types_map(model: Type[pydantic.BaseModel]) -> _TypesMap:
    queue = collections.deque([model])
    types_map: dict[str, dict[str, str]] = {}

    while len(queue):
        model = queue.popleft()
        model_type = _class_fqn(model)

        if model_type in types_map:
            continue

        types_map[model_type] = {}

        for field in model.__fields__.values():
            if issubclass(field.type_, pydantic.BaseModel):
                types_map[model_type][field.name] = _class_fqn(field.type_)
                queue.append(field.type_)

    return types_map


def _metadata_to_types_map(metadata: _Metadata) -> _TypesMap:
    types_map: _TypesMap = {}

    if isinstance(metadata, descriptor.Descriptor):
        types_map = _protobuf_to_types_map(metadata)
    elif issubclass(metadata, pydantic.BaseModel):
        types_map = _pydantic_to_types_map(metadata)

    return types_map
