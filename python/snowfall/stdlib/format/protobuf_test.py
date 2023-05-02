import datetime
import zoneinfo

import isodate
import pytest
from aiofiles import tempfile
from dateutil import tz
from google.protobuf import duration_pb2, timestamp_pb2

from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import date_pb2, datetime_pb2, testing_pb2

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

    def test_deserialize_memoryview(self) -> None:
        blob = memoryview(
            b"\n-type.googleapis.com/google.protobuf.Timestamp\x12\x06\x08\xb7\x92\xef"
            + b"\x8d\x06",
        )
        message = protobuf.AnySerializer[timestamp_pb2.Timestamp].deserialize(blob)
        assert isinstance(message, timestamp_pb2.Timestamp)
        assert message.seconds == _seconds


async def test_dump_load() -> None:
    protos = [
        timestamp_pb2.Timestamp(seconds=0),
        timestamp_pb2.Timestamp(seconds=1337),
    ]

    async with tempfile.NamedTemporaryFile("wb+") as tmp:
        for dump_proto in protos:
            await protobuf.dump(dump_proto, tmp)

        await tmp.seek(0)

        async for load_proto in protobuf.load(tmp, timestamp_pb2.Timestamp):
            protos.remove(load_proto)

    assert not protos


def test_enum_value_to_slug() -> None:
    assert (
        protobuf.enum_value_to_slug(
            testing_pb2.PascalCaseEnum.PascalCase.DESCRIPTOR,
            testing_pb2.PascalCaseEnum.PascalCase.PASCAL_CASE_UNSPECIFIED,
        )
        == "unspecified"
    )

    assert (
        protobuf.enum_value_to_slug(
            testing_pb2.PascalCaseEnum.PascalCase.DESCRIPTOR,
            testing_pb2.PascalCaseEnum.PascalCase.PASCAL_CASE_MULTI_WORD,
        )
        == "multi-word"
    )


def test_slug_to_enum_value() -> None:
    assert (
        protobuf.slug_to_enum_value(
            testing_pb2.PascalCaseEnum.PascalCase,
            "unspecified",
        )
        == testing_pb2.PascalCaseEnum.PascalCase.PASCAL_CASE_UNSPECIFIED
    )

    assert (
        protobuf.slug_to_enum_value(
            testing_pb2.PascalCaseEnum.PascalCase,
            "multi-word",
        )
        == testing_pb2.PascalCaseEnum.PascalCase.PASCAL_CASE_MULTI_WORD
    )

    with pytest.raises(ValueError, match="has no value defined for name"):
        protobuf.slug_to_enum_value(
            testing_pb2.PascalCaseEnum.PascalCase,
            "foobar",
        )


@pytest.mark.parametrize(
    ("date", "expected"),
    [
        (
            datetime.date(year=1984, month=2, day=3),
            date_pb2.Date(year=1984, month=2, day=3),
        ),
    ],
)
def test_date_to_protobuf(date: datetime.date, expected: date_pb2.Date) -> None:
    assert protobuf.date_to_protobuf(date) == expected


@pytest.mark.parametrize(
    ("proto", "expected"),
    [
        (
            datetime_pb2.DateTime(
                year=1970,
                month=1,
                day=1,
                hours=4,
                minutes=5,
                seconds=6,
                nanos=7000,
                time_zone=datetime_pb2.TimeZone(id="Europe/Berlin"),
            ),
            datetime.date(year=1970, month=1, day=1),
        ),
        (
            date_pb2.Date(year=1984, month=2, day=3),
            datetime.date(year=1984, month=2, day=3),
        ),
    ],
)
def test_protobuf_to_date(
    proto: date_pb2.Date | datetime_pb2.DateTime,
    expected: datetime.date,
) -> None:
    assert protobuf.protobuf_to_date(proto) == expected


@pytest.mark.parametrize(
    ("proto", "expected"),
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
    ("timestamp", "expected"),
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
            timestamp_pb2.Timestamp(seconds=444625506, nanos=7000),
        ),
    ],
)
def test_datetime_to_protobuf(
    timestamp: datetime.datetime,
    expected: timestamp_pb2.Timestamp,
) -> None:
    assert protobuf.datetime_to_protobuf(timestamp) == expected


@pytest.mark.parametrize(
    ("timestamp", "expected"),
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


def test_datetime_to_protobuf_datetime_with_naive_datetime() -> None:
    with pytest.raises(RuntimeError):
        protobuf.datetime_to_protobuf_datetime(datetime.datetime.now())
