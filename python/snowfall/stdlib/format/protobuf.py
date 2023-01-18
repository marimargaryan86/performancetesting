import datetime
import struct
import zoneinfo
from typing import AsyncIterator, Generic, Optional, Type, TypeVar, cast

from aiofiles.threadpool import binary
from dateutil import tz
from google.protobuf import (
    any_pb2,
    descriptor,
    duration_pb2,
    message,
    symbol_database,
    timestamp_pb2,
)

from snowfall.stdlib import string
from snowfall.stdlib.v1alpha import datetime_pb2, models_pb2

_Proto = TypeVar("_Proto", bound=message.Message)


class AnySerializer(Generic[_Proto]):
    _db = symbol_database.Default()

    @classmethod
    def serialize(cls, msg: _Proto) -> bytes:
        any_message = any_pb2.Any()

        any_message.Pack(msg)

        return any_message.SerializeToString()

    @classmethod
    def deserialize(cls, blob: bytes | memoryview) -> _Proto:
        packed_message = any_pb2.Any()

        if isinstance(blob, memoryview):
            blob = blob.tobytes()

        packed_message.ParseFromString(blob)

        symbol = cast(Type[_Proto], cls._db.GetSymbol(packed_message.TypeName()))
        unpacked_message = symbol()

        packed_message.Unpack(unpacked_message)

        return unpacked_message


async def dump(proto: message.Message, pointer: binary.AsyncBufferedIOBase) -> None:
    wire = proto.SerializeToString()

    await pointer.write(struct.pack("<L", len(wire)))
    await pointer.write(wire)


async def load(
    pointer: binary.AsyncBufferedIOBase,
    proto: Type[_Proto],
) -> AsyncIterator[_Proto]:
    while True:
        packed = await pointer.read(4)

        if len(packed) < 4:
            break

        length = struct.unpack("<L", packed)[0]
        msg = proto()

        msg.ParseFromString(await pointer.read(length))

        yield msg


def datetime_to_protobuf(timestamp: datetime.datetime) -> timestamp_pb2.Timestamp:
    proto = timestamp_pb2.Timestamp()
    proto.FromDatetime(timestamp)

    return proto


def datetime_to_protobuf_datetime(
    timestamp: datetime.datetime,
) -> datetime_pb2.DateTime:
    time_zone: Optional[datetime_pb2.TimeZone] = None
    utc_offset: Optional[duration_pb2.Duration] = None
    timestamp_offset = timestamp.utcoffset()

    if timestamp_offset is None:
        raise RuntimeError("Naive datetime objects are not supported")

    if timestamp.tzname() == "UTC":
        time_zone = datetime_pb2.TimeZone(id="UTC")
    elif isinstance(timestamp.tzinfo, zoneinfo.ZoneInfo):
        time_zone = datetime_pb2.TimeZone(
            id=timestamp.tzinfo.key,
        )
    else:
        utc_offset = duration_pb2.Duration(
            seconds=int(timestamp_offset.total_seconds()),
        )

    return datetime_pb2.DateTime(
        year=timestamp.year,
        month=timestamp.month,
        day=timestamp.day,
        hours=timestamp.hour,
        minutes=timestamp.minute,
        seconds=timestamp.second,
        nanos=timestamp.microsecond * 1000,
        time_zone=time_zone,
        utc_offset=utc_offset,
    )


def protobuf_to_datetime(
    proto: timestamp_pb2.Timestamp | datetime_pb2.DateTime,
) -> datetime.datetime:
    tzinfo: datetime.tzinfo

    if isinstance(proto, timestamp_pb2.Timestamp):
        return proto.ToDatetime(tzinfo=datetime.timezone.utc)

    if proto.HasField("time_zone"):
        tzinfo = zoneinfo.ZoneInfo(proto.time_zone.id)
    else:
        delta = datetime.timedelta(seconds=proto.utc_offset.seconds)
        tzinfo = tz.tzoffset(
            "UTC{symbol}{hours:02d}:{minutes:02d}".format(
                symbol="+" if delta.total_seconds() >= 0 else "-",
                hours=delta.seconds // 60 * 60,
                minutes=(delta.seconds // 60) % 60,
            ),
            delta.total_seconds(),
        )

    return datetime.datetime(
        year=proto.year,
        month=proto.month,
        day=proto.day,
        hour=proto.hours,
        minute=proto.minutes,
        second=proto.seconds,
        microsecond=proto.nanos // 1000,
        tzinfo=tzinfo,
    )


def date_to_protobuf(date: datetime.date) -> models_pb2.Date:
    return models_pb2.Date(
        year=date.year,
        month=date.month,
        day=date.day,
    )


def protobuf_to_date(
    proto: models_pb2.Date | datetime_pb2.DateTime,
) -> datetime.date:
    return datetime.date(year=proto.year, month=proto.month, day=proto.day)


def enum_value_to_slug(
    enum_descriptor: descriptor.EnumDescriptor,
    enum_value: int,
) -> str:
    name = enum_descriptor.values_by_number[enum_value].name.removeprefix(
        "{0}_".format(enum_descriptor.name.upper()),
    )

    return name.lower().replace("_", "-")


def slug_to_enum_value(
    enum_descriptor: descriptor.EnumDescriptor,
    name: str,
) -> int:
    enum_name = "{0}_{1}".format(
        string.to_snake(enum_descriptor.name).upper(),
        name.replace("-", "_").upper(),
    )

    return enum_descriptor.values_by_name[enum_name].number
