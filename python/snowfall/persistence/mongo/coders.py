import abc
import copy
from typing import Any, Generic, Type, TypeVar

import pydantic
import rapidjson
from google.protobuf import json_format, message

from snowfall.persistence.mongo import normalizers

Model = TypeVar("Model", bound=pydantic.BaseModel)
Proto = TypeVar("Proto", bound=message.Message)
Record = TypeVar("Record")

_mongo_id_key = "_id"
_proto_id_key = "id"
_pydantic_id_key = "id"


class BaseCoder(Generic[Record], abc.ABC):
    @abc.abstractmethod
    def decode(self, as_dict: dict[str, Any]) -> Record:
        raise NotImplementedError()

    @abc.abstractmethod
    def encode(self, record: Record) -> dict[str, Any]:
        raise NotImplementedError()


class NoopCoder(BaseCoder[dict[str, Any]]):
    def decode(self, as_dict: dict[str, Any]) -> dict[str, Any]:
        return as_dict

    def encode(self, record: dict[str, Any]) -> dict[str, Any]:
        return record


class ProtoCoder(Generic[Proto], BaseCoder[Proto]):
    _normalizers = (
        normalizers.CoordinatesNormalizer(),
        normalizers.TimestampNormalizer(),
    )

    def __init__(self, proto: Type[Proto]):
        self._proto = proto

    def decode(self, as_dict: dict[str, Any]) -> Proto:
        proto = self._proto()
        fields = proto.DESCRIPTOR.fields_by_name.keys()
        as_dict = copy.deepcopy(as_dict)

        # MongoDB stores ID in "_id", so move it to "id" if it exists on the proto.
        if _mongo_id_key in as_dict:
            id_value = as_dict.pop(_mongo_id_key)

            if _proto_id_key in fields:
                as_dict[_proto_id_key] = id_value

        for normalizer in self._normalizers:
            as_dict = normalizer.denormalize(proto.DESCRIPTOR, as_dict)

        return json_format.ParseDict(as_dict, proto, ignore_unknown_fields=True)

    def encode(self, proto: Proto) -> dict[str, Any]:
        fields = proto.DESCRIPTOR.fields_by_name.keys()

        # Only set created if it hasn't been set already.
        if "created_at" in fields and proto.created.seconds == 0:  # type: ignore[attr-defined]
            proto.created_at.GetCurrentTime()  # type: ignore[attr-defined]

        if "updated_at" in fields:
            proto.updated_at.GetCurrentTime()  # type: ignore[attr-defined]

        as_dict = json_format.MessageToDict(
            proto,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
        )

        # MongoDB expects ID to be found in "_id".
        if _proto_id_key in fields and _proto_id_key in as_dict:
            as_dict[_mongo_id_key] = as_dict.pop(_proto_id_key)

        for normalizer in self._normalizers:
            as_dict = normalizer.normalize(proto.DESCRIPTOR, as_dict)

        return as_dict


class PydanticCoder(Generic[Model], BaseCoder[Model]):
    def __init__(self, model: Type[Model]):
        self._model = model

    def decode(self, as_dict: dict[str, Any]) -> Model:
        # MongoDB stores ID in "_id", so move it to "id" if it exists on the model.
        if _mongo_id_key in as_dict:
            id_value = as_dict.pop(_mongo_id_key)

            if _pydantic_id_key in self._model.__fields__:
                as_dict[_pydantic_id_key] = id_value

        return self._model.parse_raw(rapidjson.dumps(as_dict))

    def encode(self, model: Model) -> dict[str, Any]:
        as_dict = rapidjson.loads(
            model.json(
                exclude_defaults=True,
                exclude_none=True,
            ),
        )

        # MongoDB expects ID to be found in "_id".
        if _pydantic_id_key in self._model.__fields__ and _pydantic_id_key in as_dict:
            as_dict[_mongo_id_key] = as_dict.pop(_pydantic_id_key)

        return as_dict
