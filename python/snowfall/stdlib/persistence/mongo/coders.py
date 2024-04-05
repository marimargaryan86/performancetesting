import abc
import contextlib
from collections.abc import Mapping
from typing import Any, Generic, Protocol, TypeGuard, TypeVar, cast

import pydantic
from google.protobuf import json_format, message, timestamp_pb2

from snowfall.stdlib.persistence.mongo import normalizers

Model = TypeVar("Model", bound=pydantic.BaseModel)
Proto = TypeVar("Proto", bound=message.Message)
Record = TypeVar("Record")


class _ProtoWithCreatedAt(Protocol):
    created_at: timestamp_pb2.Timestamp


class BaseCoder(Generic[Record], abc.ABC):
    @abc.abstractmethod
    def decode(self, as_dict: Mapping[str, Any]) -> Record:
        raise NotImplementedError()

    @abc.abstractmethod
    def encode(self, record: Record) -> dict[str, Any]:
        raise NotImplementedError()


class NoopCoder(BaseCoder[Mapping[str, Any]]):
    def decode(self, as_dict: Mapping[str, Any]) -> dict[str, Any]:
        return dict(as_dict)

    def encode(self, record: Mapping[str, Any]) -> dict[str, Any]:
        return dict(record)


class ProtoCoder(Generic[Proto], BaseCoder[Proto]):
    def __init__(self, proto: type[Proto]):
        self._proto = proto

    def decode(self, as_dict: Mapping[str, Any]) -> Proto:
        proto = self._proto()
        as_dict = normalizers.denormalize(proto.DESCRIPTOR, as_dict)

        return json_format.ParseDict(as_dict, proto, ignore_unknown_fields=True)

    def encode(self, proto: Proto) -> dict[str, Any]:
        # Only set created if it hasn't been set already.
        if self._is_new(proto):
            proto.created_at.GetCurrentTime()

        if hasattr(proto, "updated_at"):  # noqa: WPS421
            proto.updated_at.GetCurrentTime()

        as_dict = json_format.MessageToDict(
            proto,
            including_default_value_fields=True,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
        )

        return normalizers.normalize(proto.DESCRIPTOR, as_dict)

    def _is_new(self, proto: Proto) -> TypeGuard[_ProtoWithCreatedAt]:
        return (
            hasattr(proto, "created_at")  # noqa: WPS421
            and proto.created_at.seconds == 0
        )


class PydanticCoder(Generic[Model], BaseCoder[Model]):
    def __init__(self, model: type[Model]):
        self._model = model

    def decode(self, as_dict: Mapping[str, Any]) -> Model:
        as_dict = cast(
            dict[str, str],
            normalizers.denormalize(self._model, as_dict),
        )

        with contextlib.suppress(KeyError):
            as_dict["id"] = str(as_dict["id"])

        return self._model.model_validate(as_dict)

    def encode(self, model: Model) -> dict[str, Any]:
        as_dict = model.model_dump(mode="json")

        return normalizers.normalize(self._model, as_dict)
