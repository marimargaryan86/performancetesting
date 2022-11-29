import abc
import contextlib
from typing import Any, Generic, Mapping, Type, TypeVar, cast

import orjson
import pydantic
from google.protobuf import json_format, message

from snowfall.stdlib.persistence.mongo import normalizers

Model = TypeVar("Model", bound=pydantic.BaseModel)
Proto = TypeVar("Proto", bound=message.Message)
Record = TypeVar("Record")


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
    def __init__(self, proto: Type[Proto]):
        self._proto = proto

    def decode(self, as_dict: Mapping[str, Any]) -> Proto:
        proto = self._proto()
        as_dict = normalizers.denormalize(proto.DESCRIPTOR, as_dict)

        return json_format.ParseDict(as_dict, proto, ignore_unknown_fields=True)

    def encode(self, proto: Proto) -> dict[str, Any]:
        fields = proto.DESCRIPTOR.fields_by_name.keys()

        # Only set created if it hasn't been set already.
        if (  # noqa: WPS337
            "created_at" in fields and proto.created_at.seconds == 0  # type: ignore[attr-defined]  # noqa: B950
        ):
            proto.created_at.GetCurrentTime()  # type: ignore[attr-defined]

        if "updated_at" in fields:
            proto.updated_at.GetCurrentTime()  # type: ignore[attr-defined]

        as_dict = json_format.MessageToDict(
            proto,
            including_default_value_fields=True,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
        )

        return normalizers.normalize(proto.DESCRIPTOR, as_dict)


class PydanticCoder(Generic[Model], BaseCoder[Model]):
    def __init__(self, model: Type[Model]):
        self._model = model

    def decode(self, as_dict: Mapping[str, Any]) -> Model:
        as_dict = cast(
            dict[str, str],
            normalizers.denormalize(self._model, as_dict),
        )

        with contextlib.suppress(KeyError):
            as_dict["id"] = str(as_dict["id"])

        return self._model.parse_raw(orjson.dumps(as_dict))

    def encode(self, model: Model) -> dict[str, Any]:
        as_dict = dict(
            orjson.loads(
                model.json(
                    exclude_defaults=True,
                    exclude_none=True,
                ),
            ),
        )

        return normalizers.normalize(self._model, as_dict)
