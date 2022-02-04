import datetime

from google.protobuf import timestamp_pb2


async def datetime_to_protobuf(timestamp: datetime.datetime) -> timestamp_pb2.Timestamp:
    proto = timestamp_pb2.Timestamp()
    proto.FromDatetime(timestamp)

    return proto


async def protobuf_to_datetime(proto: timestamp_pb2.Timestamp) -> datetime.datetime:
    return proto.ToDatetime().astimezone(datetime.timezone.utc)
