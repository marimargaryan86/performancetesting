import abc
import datetime
from copy import deepcopy
from typing import Any, Callable

from asyncstdlib import functools
from dateutil import parser
from google.protobuf import descriptor, timestamp_pb2

from snowfall import dictionary
from snowfall.common.v1alpha import models_pb2


@functools.cache
async def _analyze_metadata(
    metadata: descriptor.Descriptor,
    expected: str,
) -> set[str]:
    if metadata.full_name == expected:
        return {""}

    fields = set({})

    for field in metadata.fields:
        if field.message_type:
            for path in await _analyze_metadata(field.message_type, expected):
                fields.add("{0}.{1}".format(field.name, path).rstrip("."))

    return fields


class _Normalizer(abc.ABC):
    def __init__(self) -> None:
        self._cache: set[str] = set({})

    async def normalize(
        self,
        metadata: descriptor.Descriptor,
        as_dict: Any,
    ) -> Any:
        return await self._transform(metadata, as_dict, self._normalize_value)

    async def denormalize(
        self,
        metadata: descriptor.Descriptor,
        as_dict: Any,
    ) -> Any:
        return await self._transform(metadata, as_dict, self._denormalize_value)

    async def _transform(
        self,
        metadata: descriptor.Descriptor,
        as_dict: Any,
        function: Callable[[Any], Any],
    ) -> Any:
        as_dict = deepcopy(as_dict)
        analyzed = await _analyze_metadata(metadata, await self._full_name())

        for path in analyzed:
            if path:
                await dictionary.set_nested_value(as_dict, path.split("."), function)
            else:
                as_dict = await function(as_dict)

        return as_dict

    @abc.abstractmethod
    async def _denormalize_value(self, normalized_value: Any) -> Any:
        raise NotImplementedError()

    @abc.abstractmethod
    async def _full_name(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    async def _normalize_value(self, denormalized_value: Any) -> Any:
        raise NotImplementedError()


class CoordinatesNormalizer(_Normalizer):
    async def _denormalize_value(
        self,
        normalized_value: dict[str, Any],
    ) -> dict[str, float]:
        return {
            "latitude": normalized_value["coordinates"][1],
            "longitude": normalized_value["coordinates"][0],
        }

    async def _full_name(self) -> str:
        return models_pb2.Coordinates().DESCRIPTOR.full_name

    async def _normalize_value(
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
    async def _denormalize_value(self, normalized_value: datetime.datetime) -> str:
        return normalized_value.isoformat()

    async def _full_name(self) -> str:
        return timestamp_pb2.Timestamp().DESCRIPTOR.full_name

    async def _normalize_value(self, denormalized_value: str) -> datetime.datetime:
        return parser.isoparse(denormalized_value)
