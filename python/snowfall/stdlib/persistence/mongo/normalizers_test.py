import datetime

from google.protobuf import json_format, timestamp_pb2

from snowfall.common.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import normalizers

_LATITUDE = 59.85882
_LONGITUDE = 17.63889


def test_coordinates_normalizer() -> None:
    normalizer = normalizers.CoordinatesNormalizer()
    expected = models_pb2.Coordinates(latitude=_LATITUDE, longitude=_LONGITUDE)

    normalized = normalizer.normalize(
        models_pb2.Coordinates.DESCRIPTOR,
        json_format.MessageToDict(expected, preserving_proto_field_name=True),
    )

    assert normalized == {"type": "Point", "coordinates": [_LONGITUDE, _LATITUDE]}

    actual: models_pb2.Coordinates = json_format.ParseDict(
        normalizer.denormalize(
            models_pb2.Coordinates.DESCRIPTOR,
            normalized,
        ),
        models_pb2.Coordinates(),
    )

    assert expected == actual


def test_timestamp_normalizer() -> None:
    expected_dt = datetime.datetime.now()
    normalizer = normalizers.TimestampNormalizer()
    expected_ts = timestamp_pb2.Timestamp()

    expected_ts.FromDatetime(expected_dt)

    normalized = normalizer.normalize(
        timestamp_pb2.Timestamp.DESCRIPTOR,
        json_format.MessageToDict(expected_ts, preserving_proto_field_name=True),
    )

    assert isinstance(normalized, datetime.datetime)

    actual_ts: timestamp_pb2.Timestamp = json_format.ParseDict(
        normalizer.denormalize(
            timestamp_pb2.Timestamp.DESCRIPTOR,
            normalized,
        ),
        timestamp_pb2.Timestamp(),
    )

    assert expected_dt == actual_ts.ToDatetime()
