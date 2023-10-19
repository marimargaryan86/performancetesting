import datetime

from google.protobuf import json_format, timestamp_pb2

from snowfall.stdlib.persistence.mongo import normalizers
from snowfall.stdlib.v1 import latlng_pb2, testing_pb2

_MONGO_ID_KEY = "_id"
_LATITUDE = 59.85882
_LONGITUDE = 17.63889


def test_id_normalizer() -> None:
    expected = testing_pb2.Foobar(id="foobar")
    normalized = normalizers.normalize(
        testing_pb2.Foobar.DESCRIPTOR,
        json_format.MessageToDict(expected, preserving_proto_field_name=True),
    )

    assert normalized == {_MONGO_ID_KEY: "foobar"}

    actual: testing_pb2.Foobar = json_format.ParseDict(
        normalizers.denormalize(testing_pb2.Foobar.DESCRIPTOR, normalized),
        testing_pb2.Foobar(),
    )

    assert expected == actual


def test_id_normalizer_nested() -> None:
    expected = testing_pb2.RepeatedFoobar(foobars=[testing_pb2.Foobar(id="foobar")])
    normalized = normalizers.normalize(
        testing_pb2.RepeatedFoobar.DESCRIPTOR,
        json_format.MessageToDict(expected, preserving_proto_field_name=True),
    )

    assert normalized == {"foobars": [{_MONGO_ID_KEY: "foobar"}]}

    actual: testing_pb2.RepeatedFoobar = json_format.ParseDict(
        normalizers.denormalize(testing_pb2.RepeatedFoobar.DESCRIPTOR, normalized),
        testing_pb2.RepeatedFoobar(),
    )

    assert expected == actual


def test_latlng_normalizer() -> None:
    expected = latlng_pb2.LatLng(latitude=_LATITUDE, longitude=_LONGITUDE)
    normalized = normalizers.normalize(
        latlng_pb2.LatLng.DESCRIPTOR,
        json_format.MessageToDict(expected, preserving_proto_field_name=True),
    )

    assert normalized == {"type": "Point", "coordinates": [_LONGITUDE, _LATITUDE]}

    actual: latlng_pb2.LatLng = json_format.ParseDict(
        normalizers.denormalize(latlng_pb2.LatLng.DESCRIPTOR, normalized),
        latlng_pb2.LatLng(),
    )

    assert expected == actual


def test_timestamp_normalizer() -> None:
    expected_dt = datetime.datetime.now(tz=datetime.UTC)
    expected_ts = timestamp_pb2.Timestamp()
    expected_ts.FromDatetime(expected_dt)
    normalized = normalizers.normalize(
        timestamp_pb2.Timestamp.DESCRIPTOR,
        json_format.MessageToDict(expected_ts, preserving_proto_field_name=True),
    )

    actual_ts: timestamp_pb2.Timestamp = json_format.ParseDict(
        normalizers.denormalize(timestamp_pb2.Timestamp.DESCRIPTOR, normalized),
        timestamp_pb2.Timestamp(),
    )

    assert expected_dt == actual_ts.ToDatetime(tzinfo=datetime.UTC)
