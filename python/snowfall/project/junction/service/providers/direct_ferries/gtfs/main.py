import contextlib
import pathlib
import random

import aioredis
import httpx
from motor import motor_asyncio

from snowfall.project.junction.service.providers.direct_ferries.gtfs import (
    converter as gtfs_converter,
)
from snowfall.project.junction.service.providers.direct_ferries.gtfs.gtfs_generator import (
    GTFSGenerator,
)
from snowfall.project.junction.service.providers.direct_ferries.gtfs.settings import (
    DFSetting,
)
from snowfall.project.junction.service.providers.direct_ferries.gtfs.timetables import (
    TimetableRepository,
)
from snowfall.project.junction.service.schedules import export, schedules
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base


async def _create_gtfs(app: service.Application[DFSetting]) -> None:
    output_path = pathlib.Path(app.settings.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(timeout=app.settings.timeout),
        )
        settings = app.settings

        timetable_repository = TimetableRepository(
            df_client=client.DFClient(
                auth_client=auth.AuthClient(
                    api_url=settings.affiliate_api_url,
                    client_secret=settings.client_secret,
                    client_id=settings.client_id,
                    http_client=http_client,
                ),
                http_client=http_client,
                config=base.ClientConfig(
                    api_url=settings.api_url,
                    partner_code=settings.partner_code,
                    client_id=settings.client_id,
                    client_secret=settings.client_secret,
                    timeout=settings.timeout,
                ),
            ),
        )

        timetables_data = await timetable_repository.get_timetables()

    converter = gtfs_converter.DFDataConverter(
        timetables_data=timetables_data,
    )
    await GTFSGenerator().generate_feed(converter)

    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    pool = aioredis.from_url(random.choice(app.settings.redis_dsn))  # nosec

    async with pool.client() as conn:  # nosec
        await export.Exporter(
            redis.Client[bytes](conn, app.name),
            schedules.ScheduleRepository(mongo.schedules.schedules),
            always_run=app.settings.always_run,
        ).export(output_path)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="gtfs_generator")
    entrypoint.enter_with_commands(
        service.Command(
            name="export",
            callback=_create_gtfs,
            settings_class=DFSetting,
        ),
    )
