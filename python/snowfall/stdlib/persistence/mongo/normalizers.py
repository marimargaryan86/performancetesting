import abc
import collections
import datetime
import functools
import inspect
import types
from collections.abc import Mapping, Sequence
from enum import IntEnum
from typing import Any, TypeVar, cast, get_args, get_origin

import pydantic
from dateutil import parser
from google.protobuf import descriptor, timestamp_pb2

from snowfall.stdlib.v1 import latlng_pb2

AnyValue = TypeVar("AnyValue", bound=Any)

_Metadata = descriptor.Descriptor | type[pydantic.BaseModel]
_TypesMap = Mapping[str, Mapping[str, str]]

_MONGO_ID_KEY = "_id"
_MODEL_ID_KEY = "id"
_LAT_KEY = "latitude"
_LON_KEY = "longitude"
_COORDINATES_KEY = "coordinates"


class Normalizer(abc.ABC):
    @abc.abstractmethod
    def normalize(self, maybe_dict: AnyValue) -> AnyValue:
        """Normalize a value."""

    @abc.abstractmethod
    def denormalize(self, maybe_dict: AnyValue) -> AnyValue:
        """Denormalize a value."""

    @abc.abstractmethod
    def supports(self, fqn: str) -> bool:
        """Return whether this normalizer supports normalizing a specific FQN."""


class _IdNormalizer(Normalizer):
    def denormalize(
        self,
        maybe_dict: AnyValue,
    ) -> AnyValue:
        if isinstance(maybe_dict, dict) and _MONGO_ID_KEY in maybe_dict:
            maybe_dict[_MODEL_ID_KEY] = maybe_dict.pop(_MONGO_ID_KEY)

        return cast(AnyValue, maybe_dict)

    def supports(self, fqn: str) -> bool:
        return True

    def normalize(
        self,
        maybe_dict: AnyValue,
    ) -> AnyValue:
        if isinstance(maybe_dict, dict) and _MODEL_ID_KEY in maybe_dict:
            maybe_dict[_MONGO_ID_KEY] = maybe_dict.pop(_MODEL_ID_KEY)

        return cast(AnyValue, maybe_dict)


class _LatLngNormalizer(Normalizer):
    def denormalize(
        self,
        maybe_dict: AnyValue,
    ) -> AnyValue:
        return cast(
            AnyValue,
            {
                _LAT_KEY: maybe_dict[_COORDINATES_KEY][1],
                _LON_KEY: maybe_dict[_COORDINATES_KEY][0],
            },
        )

    def supports(self, fqn: str) -> bool:
        return fqn == latlng_pb2.LatLng().DESCRIPTOR.full_name

    def normalize(
        self,
        maybe_dict: AnyValue,
    ) -> AnyValue:
        return cast(
            AnyValue,
            {
                "type": "Point",
                _COORDINATES_KEY: [
                    maybe_dict[_LON_KEY],
                    maybe_dict[_LAT_KEY],
                ],
            },
        )


class _TimestampNormalizer(Normalizer):
    def denormalize(
        self,
        maybe_dict: AnyValue,
    ) -> AnyValue:
        if not maybe_dict.tzinfo:
            maybe_dict = maybe_dict.replace(tzinfo=datetime.UTC)

        return maybe_dict.isoformat()

    def supports(self, fqn: str) -> bool:
        return fqn == timestamp_pb2.Timestamp().DESCRIPTOR.full_name

    def normalize(
        self,
        maybe_dict: AnyValue,
    ) -> AnyValue:
        return cast(AnyValue, parser.isoparse(maybe_dict))


class _NormalizerMode(IntEnum):
    normalize = 1
    denormalize = 2


_additional: list[Normalizer] = []
_normalizers: list[Normalizer] = [
    _IdNormalizer(),
    _LatLngNormalizer(),
    _TimestampNormalizer(),
]


def register(normalizer: Normalizer) -> None:
    if isinstance(normalizer, tuple(type(registered) for registered in _additional)):
        return

    _additional.append(normalizer)


def normalize(metadata: _Metadata, maybe_dict: AnyValue) -> AnyValue:
    return _transform(
        _metadata_fqn(metadata),
        _metadata_to_types_map(metadata),
        maybe_dict,
        _NormalizerMode.normalize,
    )


def denormalize(metadata: _Metadata, maybe_dict: AnyValue) -> AnyValue:
    return _transform(
        _metadata_fqn(metadata),
        _metadata_to_types_map(metadata),
        maybe_dict,
        _NormalizerMode.denormalize,
    )


def _apply_normalizers(
    fqn: str,
    mode: _NormalizerMode,
    maybe_dict: AnyValue,
) -> AnyValue:
    assert mode in {  # noqa: S101
        _NormalizerMode.normalize,
        _NormalizerMode.denormalize,
    }
    if mode is _NormalizerMode.normalize:
        normalizers = (*_additional, *_normalizers)
    else:
        normalizers = (*_normalizers, *_additional)

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
    maybe_dict: AnyValue,
    mode: _NormalizerMode,
) -> AnyValue:
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

    return cast(AnyValue, maybe_dict)


def _class_fqn(type_: type[object]) -> str:
    return "{0}.{1}".format(type_.__module__, type_.__name__)


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
def _pydantic_to_types_map(
    model: type[pydantic.BaseModel],
) -> _TypesMap:
    queue = collections.deque([model])
    types_map: dict[str, dict[str, str]] = {}

    while len(queue):
        model = queue.popleft()
        model_type = _class_fqn(model)

        if model_type in types_map:
            continue

        types_map[model_type] = {}

        for field_name, field in model.model_fields.items():
            maybe_pydantic = _maybe_get_pydantic_model(field.annotation)

            if maybe_pydantic:
                types_map[model_type][field_name] = _class_fqn(maybe_pydantic)
                queue.append(maybe_pydantic)

    return types_map


def _maybe_get_pydantic_model(
    annotation: type[Any] | None,
) -> type[pydantic.BaseModel] | None:
    if inspect.isclass(annotation) and issubclass(annotation, pydantic.BaseModel):
        return annotation

    if get_origin(annotation) not in {list, Sequence, types.UnionType}:
        return None

    all_pydantic_args = {
        arg
        for arg in get_args(annotation)
        if isinstance(arg, type) and issubclass(arg, pydantic.BaseModel)
    }

    if len(all_pydantic_args) > 1:
        raise NotImplementedError("Complex types are not yet supported.")

    return next(iter(all_pydantic_args)) if all_pydantic_args else None


def _metadata_to_types_map(metadata: _Metadata) -> _TypesMap:
    types_map: _TypesMap = {}

    if isinstance(metadata, descriptor.Descriptor):
        types_map = _protobuf_to_types_map(metadata)
    elif issubclass(metadata, pydantic.BaseModel):
        types_map = _pydantic_to_types_map(metadata)

    return types_map
