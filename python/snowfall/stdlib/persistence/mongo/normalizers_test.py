import datetime

import freezegun
import pytest
from google.protobuf import timestamp_pb2

from snowfall.stdlib.persistence.mongo import coders, testing
from snowfall.stdlib.v1 import latlng_pb2

_MONGO_ID_KEY = "_id"
_LATITUDE = 59.85882
_LONGITUDE = 17.63889


def test_id_normalizer_protobuf() -> None:
    coder = coders.ProtoCoder(testing.FoobarProto)
    document = testing.FoobarProto(
        id="foobar",
        nested_foobar=testing.FoobarProto(id="bazqux"),
    )
    encoded = coder.encode(document)
    assert encoded["_id"] == "foobar"
    assert encoded["nested_foobar"]["_id"] == "bazqux"
    decoded = coder.decode(encoded)
    assert document.id == decoded.id
    assert document.nested_foobar.id == decoded.nested_foobar.id


def test_id_normalizer_pydantic() -> None:
    coder = coders.PydanticCoder(testing.FoobarModel)
    document = testing.FoobarModel(
        id="foobar",
        nested_foobar=testing.FoobarModel(id="bazqux"),
    )
    encoded = coder.encode(document)
    assert encoded["_id"] == "foobar"
    assert encoded["nested_foobar"]["_id"] == "bazqux"
    decoded = coder.decode(encoded)
    assert document.model_dump() == decoded.model_dump()


def test_id_normalizer_nested_protobuf() -> None:
    coder = coders.ProtoCoder(testing.RepeatedFoobarProto)
    document = testing.RepeatedFoobarProto(
        foobars=[
            testing.FoobarProto(
                id="foobar",
                nested_foobar=testing.FoobarProto(id="bazqux"),
            ),
        ],
    )
    encoded = coder.encode(document)
    assert encoded["foobars"][0]["_id"] == "foobar"
    assert encoded["foobars"][0]["nested_foobar"]["_id"] == "bazqux"
    decoded = coder.decode(encoded)
    assert document.foobars[0].id == decoded.foobars[0].id
    assert document.foobars[0].nested_foobar.id == decoded.foobars[0].nested_foobar.id


def test_id_normalizer_nested_pydantic() -> None:
    coder = coders.PydanticCoder(testing.RepeatedFoobarModel)
    document = testing.RepeatedFoobarModel(
        foobars=[
            testing.FoobarModel(
                id="foobar",
                nested_foobar=testing.FoobarModel(id="bazqux"),
            ),
        ],
    )
    encoded = coder.encode(document)
    assert encoded["foobars"][0]["_id"] == "foobar"
    assert encoded["foobars"][0]["nested_foobar"]["_id"] == "bazqux"
    decoded = coder.decode(encoded)
    assert document.model_dump() == decoded.model_dump()


@pytest.mark.parametrize(
    ("coder", "document"),
    [
        (
            coders.ProtoCoder(latlng_pb2.LatLng),
            latlng_pb2.LatLng(latitude=_LATITUDE, longitude=_LONGITUDE),
        ),
    ],
)
def test_latlng_normalizer(
    coder: coders.ProtoCoder[latlng_pb2.LatLng],
    document: latlng_pb2.LatLng,
) -> None:
    encoded = coder.encode(document)
    assert encoded == {"type": "Point", "coordinates": [_LONGITUDE, _LATITUDE]}
    decoded = coder.decode(encoded)
    assert document == decoded


@freezegun.freeze_time(
    datetime.datetime(year=2024, month=1, day=1, tzinfo=datetime.UTC),
)
def test_timestamp_normalizer() -> None:
    expected = datetime.datetime.now(tz=datetime.UTC)
    coder = coders.ProtoCoder(timestamp_pb2.Timestamp)
    document = timestamp_pb2.Timestamp()
    document.FromDatetime(expected)
    encoded = coder.encode(document)
    assert encoded == expected
    decoded = coder.decode(encoded)
    assert document == decoded
    assert expected == decoded.ToDatetime(tzinfo=datetime.UTC)
