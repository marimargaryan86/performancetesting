import ipaddress
import pathlib
import random

import aioredis
from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.junction.service.schedules import (
    consumer,
    export,
    grpc,
    schedules,
)
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import types
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(service.Settings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: tuple[AnyUrl]


class _ExportSettings(service.Settings):
    always_run: bool = False
    mongo_dsn: tuple[AnyUrl]
    output_path: str
    redis_dsn: tuple[AnyUrl]


class _ImportSettings(service.Settings):
    amqp_dsn: AnyUrl
    mongo_dsn: tuple[AnyUrl]


async def _export(app: service.Application[_ExportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    pool = aioredis.from_url(random.choice(app.settings.redis_dsn))  # nosec
    output_path = pathlib.Path(app.settings.output_path)

    output_path.mkdir(parents=True, exist_ok=True)

    async with pool.client() as conn:  # nosec
        await export.Exporter(
            redis.Client[bytes](conn, "exporter"),
            schedules.ScheduleRepository(mongo.schedules.schedules),
            always_run=app.settings.always_run,
        ).export(output_path)


async def _import(app: service.Application[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    async with types.Connection(app.settings.amqp_dsn) as connection:
        import_consumer = consumer.ScheduleImportConsumer(
            schedules=schedules.ScheduleRepository(mongo.schedules.schedules),
            consumer=amqp_consumer.Consumer(
                connection=connection,
                exchange=types.Exchange("schedules"),
                queue_name="{0}_schedules_importer".format(app.name),
                routing_key="schedule.import",
            ),
        )

        await import_consumer.consume()


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.ScheduleService(
                legs=schedules.LegRepository(mongo.schedules.schedules),
                schedules=schedules.ScheduleRepository(mongo.schedules.schedules),
                default_page_size=app.settings.default_page_size,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="schedules")

    entrypoint.enter_with_commands(
        service.Command(
            name="export",
            callback=_export,
            settings_class=_ExportSettings,
        ),
        service.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
