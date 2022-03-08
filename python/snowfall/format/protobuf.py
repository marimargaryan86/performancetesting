import datetime
import struct
from typing import AsyncIterator, Type, TypeVar

from aiofiles.threadpool import binary
from google.protobuf import message, timestamp_pb2

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


async def datetime_to_protobuf(timestamp: datetime.datetime) -> timestamp_pb2.Timestamp:
    proto = timestamp_pb2.Timestamp()
    proto.FromDatetime(timestamp)

    return proto


async def protobuf_to_datetime(proto: timestamp_pb2.Timestamp) -> datetime.datetime:
    return proto.ToDatetime().replace(tzinfo=datetime.timezone.utc)
