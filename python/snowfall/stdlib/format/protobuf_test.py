import datetime
import zoneinfo

import isodate
import pytest
from dateutil import tz
from google.protobuf import duration_pb2, timestamp_pb2

from snowfall.project.junction.service.places.v1alpha import (
    models_pb2 as places_models_pb2,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import datetime_pb2, models_pb2, testing_pb2

_seconds = 1639696695


class TestSerializer(object):
    def test_serialize(self) -> None:
        message = timestamp_pb2.Timestamp(seconds=_seconds)
        message_serialized = protobuf.AnySerializer.serialize(message)
        assert isinstance(message_serialized, bytes)

    def test_deserialize(self) -> None:
        blob = (
            b"\n-type.googleapis.com/google.protobuf.Timestamp\x12\x06\x08\xb7\x92\xef"
            + b"\x8d\x06"
        )
        message = protobuf.AnySerializer[timestamp_pb2.Timestamp].deserialize(blob)
        assert isinstance(message, timestamp_pb2.Timestamp)
        assert message.seconds == _seconds


def test_enum_value_to_slug() -> None:
    assert (
        protobuf.enum_value_to_slug(
            models_pb2.Schedule.Type.DESCRIPTOR,
            models_pb2.Schedule.TYPE_AIR,
        )
        == "air"
    )

    assert (
        protobuf.enum_value_to_slug(
            places_models_pb2.Location.Type.DESCRIPTOR,
            places_models_pb2.Location.TYPE_RAILWAY_STATION,
        )
        == "railway-station"
    )


def test_slug_to_enum_value() -> None:
    assert (
        protobuf.slug_to_enum_value(
            models_pb2.Schedule.Type.DESCRIPTOR,
            "air",
        )
        == models_pb2.Schedule.TYPE_AIR
    )

    assert (
        protobuf.slug_to_enum_value(
            places_models_pb2.Location.Type.DESCRIPTOR,
            "railway-station",
        )
        == places_models_pb2.Location.TYPE_RAILWAY_STATION
    )
    assert (
        protobuf.slug_to_enum_value(
            testing_pb2.PascalCaseEnum.PascalCase.DESCRIPTOR,
            "unspecified",
        )
        == 0
    )


@pytest.mark.parametrize(
    "proto, expected",
    [
        (
            timestamp_pb2.Timestamp(seconds=0),
            datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            datetime_pb2.DateTime(
                year=1984,
                month=2,
                day=3,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                time_zone=datetime_pb2.TimeZone(id="Europe/Berlin"),
            ),
            datetime.datetime(
                year=1984,
                month=2,
                day=3,
                hour=4,
                minute=5,
                second=6,
                microsecond=7,
                tzinfo=zoneinfo.ZoneInfo("Europe/Berlin"),
            ),
        ),
        (
            datetime_pb2.DateTime(
                year=1984,
                month=2,
                day=3,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                utc_offset=duration_pb2.Duration(seconds=3600),
            ),
            datetime.datetime(
                year=1984,
                month=2,
                day=3,
                hour=4,
                minute=5,
                second=6,
                microsecond=7,
                tzinfo=tz.tzoffset("UTC+01:00", 3600),
            ),
        ),
    ],
)
def test_protobuf_to_datetime(
    proto: timestamp_pb2.Timestamp | datetime_pb2.DateTime,
    expected: datetime.datetime,
) -> None:
    assert protobuf.protobuf_to_datetime(proto) == expected


@pytest.mark.parametrize(
    "timestamp, expected",
    [
        (
            datetime.datetime(
                year=1984,
                month=2,
                day=3,
                hour=4,
                minute=5,
                second=6,
                microsecond=7,
                tzinfo=zoneinfo.ZoneInfo("Europe/Berlin"),
            ),
            datetime_pb2.DateTime(
                year=1984,
                month=2,
                day=3,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                time_zone=datetime_pb2.TimeZone(id="Europe/Berlin"),
            ),
        ),
        (
            datetime.datetime(
                year=1984,
                month=2,
                day=3,
                hour=4,
                minute=5,
                second=6,
                microsecond=7,
                tzinfo=zoneinfo.ZoneInfo("America/New_York"),
            ),
            datetime_pb2.DateTime(
                year=1984,
                month=2,
                day=3,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                time_zone=datetime_pb2.TimeZone(id="America/New_York"),
            ),
        ),
        (
            datetime.datetime(
                year=1984,
                month=2,
                day=3,
                hour=4,
                minute=5,
                second=6,
                microsecond=7,
                tzinfo=datetime.timezone.utc,
            ),
            datetime_pb2.DateTime(
                year=1984,
                month=2,
                day=3,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                time_zone=datetime_pb2.TimeZone(id="UTC"),
            ),
        ),
        (
            datetime.datetime(
                year=1984,
                month=2,
                day=3,
                hour=4,
                minute=5,
                second=6,
                microsecond=7,
                tzinfo=tz.UTC,
            ),
            datetime_pb2.DateTime(
                year=1984,
                month=2,
                day=3,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                time_zone=datetime_pb2.TimeZone(id="UTC"),
            ),
        ),
        (
            datetime.datetime(
                year=1984,
                month=2,
                day=3,
                hour=4,
                minute=5,
                second=6,
                microsecond=7,
                tzinfo=isodate.tzinfo.Utc(),
            ),
            datetime_pb2.DateTime(
                year=1984,
                month=2,
                day=3,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                time_zone=datetime_pb2.TimeZone(id="UTC"),
            ),
        ),
        (
            datetime.datetime(
                year=1984,
                month=2,
                day=3,
                hour=4,
                minute=5,
                second=6,
                microsecond=7,
                tzinfo=tz.tzoffset("CET", 3600),
            ),
            datetime_pb2.DateTime(
                year=1984,
                month=2,
                day=3,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                utc_offset=duration_pb2.Duration(seconds=3600),
            ),
        ),
    ],
)
def test_datetime_to_protobuf_datetime(
    timestamp: datetime.datetime,
    expected: datetime_pb2.DateTime,
) -> None:
    assert protobuf.datetime_to_protobuf_datetime(timestamp) == expected
