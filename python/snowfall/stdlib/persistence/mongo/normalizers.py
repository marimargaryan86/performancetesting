import abc
import datetime
import functools
from copy import deepcopy
from typing import Any, Callable

from dateutil import parser
from google.protobuf import descriptor, timestamp_pb2

from snowfall import dictionary
from snowfall.common.v1alpha import models_pb2


@functools.cache
def _analyze_metadata(
    metadata: descriptor.Descriptor,
    expected: str,
) -> set[str]:
    if metadata.full_name == expected:
        return {""}

    fields = set({})

    for field in metadata.fields:
        if field.message_type:
            for path in _analyze_metadata(field.message_type, expected):
                fields.add("{0}.{1}".format(field.name, path).rstrip("."))

    return fields


class _Normalizer(abc.ABC):
    def __init__(self) -> None:
        self._cache: set[str] = set({})

    def normalize(
        self,
        metadata: descriptor.Descriptor,
        as_dict: Any,
    ) -> Any:
        return self._transform(metadata, as_dict, self._normalize_value)

    def denormalize(
        self,
        metadata: descriptor.Descriptor,
        as_dict: Any,
    ) -> Any:
        return self._transform(metadata, as_dict, self._denormalize_value)

    def _transform(
        self,
        metadata: descriptor.Descriptor,
        as_dict: Any,
        function: Callable[[Any], Any],
    ) -> Any:
        as_dict = deepcopy(as_dict)
        analyzed = _analyze_metadata(metadata, self._full_name())

        for path in analyzed:
            if path:
                dictionary.set_nested_value(as_dict, path.split("."), function)
            else:
                as_dict = function(as_dict)

        return as_dict

    @abc.abstractmethod
    def _denormalize_value(self, normalized_value: Any) -> Any:
        raise NotImplementedError()

    @abc.abstractmethod
    def _full_name(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def _normalize_value(self, denormalized_value: Any) -> Any:
        raise NotImplementedError()


class CoordinatesNormalizer(_Normalizer):
    def _denormalize_value(
        self,
        normalized_value: dict[str, Any],
    ) -> dict[str, float]:
        return {
            "latitude": normalized_value["coordinates"][1],
            "longitude": normalized_value["coordinates"][0],
        }

    def _full_name(self) -> str:
        return models_pb2.Coordinates().DESCRIPTOR.full_name

    def _normalize_value(
        self,
        denormalized_value: dict[str, float],
    ) -> dict[str, Any]:
        return {
            "type": "Point",
            "coordinates": [
                denormalized_value["longitude"],
                denormalized_value["latitude"],
            ],
        }


class TimestampNormalizer(_Normalizer):
    def _denormalize_value(self, normalized_value: datetime.datetime) -> str:
        return normalized_value.isoformat()

    def _full_name(self) -> str:
        return timestamp_pb2.Timestamp().DESCRIPTOR.full_name

    def _normalize_value(self, denormalized_value: str) -> datetime.datetime:
        return parser.isoparse(denormalized_value)
