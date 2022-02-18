import datetime

import pydantic
from dateutil import tz
from google.protobuf import timestamp_pb2

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
    coder = coders.ProtoCoder[timestamp_pb2.Timestamp](timestamp_pb2.Timestamp)
    payload = timestamp_pb2.Timestamp()
    encoded = coder.encode(payload)

    assert encoded == datetime.datetime.fromtimestamp(  # type: ignore[comparison-overlap]
        0,
        tz=tz.tzutc(),
    )
    assert payload == coder.decode(encoded)


def test_pydantic_coder() -> None:
    coder = coders.PydanticCoder[_TestModel](_TestModel)
    payload = _TestModel(name="foobar")
    encoded = coder.encode(payload)

    assert encoded == {"name": "foobar"}
    assert payload == coder.decode(encoded)
