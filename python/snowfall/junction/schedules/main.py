import ipaddress
import pathlib
import random
from typing import Optional

import aiofiles
import aioredis
import boto3
from motor import motor_asyncio
from pydantic import AnyUrl, BaseSettings

from snowfall.junction.schedules import consumer, export, grpc, schedules
from snowfall.persistence import redis
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp
from snowfall.transport import grpc as grpc_transport


class _GrpcSettings(BaseSettings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: tuple[AnyUrl]


class _ExportSettings(BaseSettings):
    aws_access_key_id: Optional[str]  # automatically used by Boto3
    aws_secret_access_key: Optional[str]  # automatically used by Boto3
    mongo_dsn: tuple[AnyUrl]
    redis_dsn: tuple[AnyUrl]
    s3_bucket_name: str = "junction-schedules-export"
    upload_to_s3: bool = False


class _ImportSettings(BaseSettings):
    amqp_dsn: tuple[AnyUrl]
    mongo_dsn: tuple[AnyUrl]


async def _export(_: RunnableService) -> None:
    settings = _ExportSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    pool = aioredis.from_url(random.choice(settings.redis_dsn))  # nosec

    async with pool.client() as conn:  # nosec
        async with aiofiles.tempfile.TemporaryDirectory() as temp:  # type: ignore[attr-defined]
            await export.Exporter(
                redis.Client(conn, "exporter"),
                schedules.ScheduleRepository(mongo.schedules.schedules),
            ).export(pathlib.Path(temp))

            if settings.upload_to_s3:
                await _upload_files(pathlib.Path(temp), settings.s3_bucket_name)


async def _upload_files(temp_path: pathlib.Path, bucket_name: str) -> None:
    s3 = boto3.client("s3")
    proto_files = (
        "route_stops.bin",
        "routes.bin",
        "schedule_stops.bin",
        "schedules.bin",
        "stops.bin",
        "transfers.bin",
    )

    for proto_file in proto_files:
        with open(str(temp_path.joinpath(proto_file)), "rb") as proto_obj:
            s3.upload_fileobj(Fileobj=proto_obj, Bucket=bucket_name, Key=proto_file)


async def _import(service: RunnableService) -> None:
    settings = _ImportSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    connection = amqp.Connection(random.choice(settings.amqp_dsn))  # nosec

    async with connection:
        import_consumer = consumer.ScheduleImportConsumer(
            schedules=schedules.ScheduleRepository(mongo.schedules.schedules),
            consumer=await amqp.create_consumer(
                conn=connection,
                exchange_name="schedules",
                queue_name="{0}_schedules_importer".format(service.name),
                routing_key="schedule.import",
            ),
        )

        await import_consumer.consume()


async def _serve(service: RunnableService) -> None:
    settings = _GrpcSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    server = grpc_transport.create_server(
        settings.grpc_address,
        settings.grpc_port,
        [
            grpc.ScheduleService(
                schedules=schedules.ScheduleRepository(mongo.schedules.schedules),
                default_page_size=settings.default_page_size,
            ),
        ],
    )

    await server.start()
    service.add_cleanup_task(server.stop(5))
    await server.wait_for_termination()


if __name__ == "__main__":
    _service = make_runnable_service(
        name="schedules",
        tasks=(
            Task(command="export", method=_export),
            Task(command="import", method=_import),
            Task(command="grpc", method=_serve),
        ),
    )

    _service.run()
