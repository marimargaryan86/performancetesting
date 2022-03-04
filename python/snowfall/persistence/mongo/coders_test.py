import datetime

import pydantic

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence.mongo import coders


class _TestModel(pydantic.BaseModel):
    name: str


def test_noop_coder() -> None:
    coder = coders.NoopCoder()
    payload = {"foo": "bar"}
    encoded = coder.encode(payload)

    assert payload == encoded
    assert payload == coder.decode(encoded)


def test_proto_coder() -> None:
    coder = coders.ProtoCoder[models_pb2.Place](models_pb2.Place)
    payload = models_pb2.Place()
    encoded = coder.encode(payload)

    assert isinstance(encoded["updated_at"], datetime.datetime)
    assert payload == coder.decode(encoded)


def test_pydantic_coder() -> None:
    coder = coders.PydanticCoder[_TestModel](_TestModel)
    payload = _TestModel(name="foobar")
    encoded = coder.encode(payload)

    assert encoded == {"name": "foobar"}
    assert payload == coder.decode(encoded)
