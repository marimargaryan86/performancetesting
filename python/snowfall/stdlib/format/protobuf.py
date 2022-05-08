import datetime
import struct
import zoneinfo
from typing import AsyncIterator, Type, TypeVar, Union

from aiofiles.threadpool import binary
from dateutil import tz
from google.protobuf import message, timestamp_pb2
from google.protobuf.descriptor import EnumDescriptor

from snowfall.common.v1alpha import datetime_pb2, models_pb2

_Proto = TypeVar("_Proto", bound=message.Message)


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
    return datetime_pb2.DateTime(
        year=timestamp.year,
        month=timestamp.month,
        day=timestamp.day,
        hours=timestamp.hour,
        minutes=timestamp.minute,
        seconds=timestamp.second,
        nanos=timestamp.microsecond * 1000,
        time_zone=datetime_pb2.TimeZone(
            id="UTC" if timestamp.tzinfo == tz.tzutc() else str(timestamp.tzinfo),
        ),
    )


def protobuf_to_datetime(
    proto: Union[timestamp_pb2.Timestamp, datetime_pb2.DateTime],
) -> datetime.datetime:
    if isinstance(proto, timestamp_pb2.Timestamp):
        return proto.ToDatetime().replace(tzinfo=datetime.timezone.utc)

    return datetime.datetime(
        year=proto.year,
        month=proto.month,
        day=proto.day,
        hour=proto.hours,
        minute=proto.minutes,
        second=proto.seconds,
        microsecond=proto.nanos // 1000,
        tzinfo=zoneinfo.ZoneInfo(proto.time_zone.id),
    )


def date_to_protobuf(date: datetime.date) -> models_pb2.Date:
    return models_pb2.Date(
        year=date.year,
        month=date.month,
        day=date.day,
    )


def protobuf_to_date(
    proto: Union[models_pb2.Date, datetime_pb2.DateTime],
) -> datetime.date:
    return datetime.date(year=proto.year, month=proto.month, day=proto.day)


def enum_value_to_slug(descriptor: EnumDescriptor, enum_value: int) -> str:
    name = descriptor.values_by_number[enum_value].name.removeprefix(
        "{0}_".format(descriptor.name.upper()),
    )

    return name.lower().replace("_", "-")


def slug_to_enum_value(descriptor: EnumDescriptor, name: str) -> int:
    enum_name = "{0}_{1}".format(descriptor.name.upper(), name.upper())

    return descriptor.values_by_name[enum_name].number
