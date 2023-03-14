import contextlib
import pathlib

import httpx

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
from snowfall.stdlib import service
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base


async def _create_gtfs(app: service.Application[DFSetting]) -> None:
    output_path = pathlib.Path(app.settings.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
        )

        timetable_repository = TimetableRepository(
            df_client=client.DfHttpClient(
                auth_client=auth.AuthClient(
                    api_url=app.settings.affiliate_api_url,
                    client_secret=app.settings.client_secret,
                    client_id=app.settings.client_id,
                    http_client=http_client,
                ),
                http_client=http_client,
                config=base.ClientConfig(
                    api_url=app.settings.api_url,
                    partner_code=app.settings.partner_code,
                    client_id=app.settings.client_id,
                    client_secret=app.settings.client_secret,
                    timeout=int(app.settings.api_timeout.total_seconds()),
                ),
            ),
        )

        timetable_responses = await timetable_repository.get_timetables()

    converter = gtfs_converter.DFDataConverter(
        timetable_responses=timetable_responses,
    )

    await GTFSGenerator(app.settings.output_path).generate_feed(converter)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="gtfs_generator")
    entrypoint.enter_with_commands(
        service.Command(
            name="export",
            callback=_create_gtfs,
            settings_class=DFSetting,
        ),
    )
