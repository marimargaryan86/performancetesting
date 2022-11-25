import contextlib
import dataclasses
import pathlib
from typing import Optional, Sequence

import httpx
import pydantic

from snowfall.project.junction.service.providers.distribusion.config import (
    DistribusionConfig,
)
from snowfall.stdlib import h3, service
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.models.stations import Station as VendorStation


class DumpStationsSettings(DistribusionConfig, service.Settings):
    output_file: str = pydantic.Field(hidden=True, argument=True)


@dataclasses.dataclass(frozen=True)
class Station(h3.CoordinatesItem):
    name: Optional[str]


async def dump_stations(app: service.Application[DumpStationsSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
            ),
        )
        distribusion_client = client.DistribusionClient(
            api_base_url=app.settings.api_base_url,
            api_key=app.settings.api_key,
            retailer_partner_number=app.settings.retailer_partner_number,
            http_client=http_client,
        )

        await _dump_stations(
            await distribusion_client.get_stations(),
            pathlib.Path(app.settings.output_file),
        )


async def _dump_stations(
    response: Sequence[VendorStation],
    output_file: pathlib.Path,
) -> None:
    pass  # noqa: WPS420


async def _load_stations() -> list[Station]:
    # todo
    return []
