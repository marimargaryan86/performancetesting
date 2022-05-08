import datetime
import zoneinfo
from typing import Union

import pytest
from dateutil import tz
from google.protobuf import timestamp_pb2

from snowfall.common.v1alpha import datetime_pb2, models_pb2
from snowfall.stdlib.format import protobuf


def test_enum_value_to_name() -> None:
    assert (
        protobuf.enum_value_to_slug(
            models_pb2.Schedule.Type.DESCRIPTOR,
            models_pb2.Schedule.TYPE_AIR,
        )
        == "air"
    )


def test_enum_name_to_value() -> None:
    assert (
        protobuf.slug_to_enum_value(
            models_pb2.Schedule.Type.DESCRIPTOR,
            "air",
        )
        == models_pb2.Schedule.TYPE_AIR
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
    ],
)
def test_protobuf_to_datetime(
    proto: Union[timestamp_pb2.Timestamp, datetime_pb2.DateTime],
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
    ],
)
def test_datetime_to_protobuf_datetime(
    timestamp: datetime.datetime,
    expected: datetime_pb2.DateTime,
) -> None:
    assert protobuf.datetime_to_protobuf_datetime(timestamp) == expected
