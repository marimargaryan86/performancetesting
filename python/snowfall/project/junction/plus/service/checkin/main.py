import ipaddress
import random
from collections.abc import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.junction.plus.service.checkin.cron import CheckinCronJob
from snowfall.project.junction.plus.service.checkin.grpc import CheckinService
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class _CronSettings(application.Settings):
    mongo_dsn: Sequence[AnyUrl]


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CheckinService(),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _cron_run(
    app: application.AsyncApplication[_CronSettings],
) -> None:
    motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    job = CheckinCronJob()

    await job.run()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="checkin")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        application.Command(
            name="cron",
            callback=_cron_run,
            settings_class=_CronSettings,
        ),
    )
