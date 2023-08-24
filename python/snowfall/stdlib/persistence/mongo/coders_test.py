import datetime

from pydantic import v1 as pydantic

from snowfall.stdlib.persistence.mongo import coders
from snowfall.stdlib.v1 import testing_pb2


class _TestModel(pydantic.BaseModel):
    name: str


def test_noop_coder() -> None:
    coder = coders.NoopCoder()
    payload = {"foo": "bar"}
    encoded = coder.encode(payload)

    assert payload == encoded
    assert payload == coder.decode(encoded)


def test_proto_coder() -> None:
    coder = coders.ProtoCoder[testing_pb2.Foobar](testing_pb2.Foobar)
    payload = testing_pb2.Foobar()
    encoded = coder.encode(payload)

    assert isinstance(encoded["updated_at"], datetime.datetime)
    assert payload == coder.decode(encoded)


def test_pydantic_coder() -> None:
    coder = coders.PydanticCoder[_TestModel](_TestModel)
    payload = _TestModel(name="foobar")
    encoded = coder.encode(payload)

    assert encoded == {"name": "foobar"}
    assert payload == coder.decode(encoded)
