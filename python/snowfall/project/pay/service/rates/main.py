import ipaddress
import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl, HttpUrl

from snowfall.project.pay.service.rates.backup_rates_cron import UpdateBackUpRatesJob
from snowfall.project.pay.service.rates.grpc import RatesService
from snowfall.project.pay.service.rates.rates import (
    BackUpRatesRepository,
    RatesRepository,
)
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.apilayer.client import APILayer


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50062
    mongo_dsn: Sequence[AnyUrl]


class _BackUpCronJobSettings(service.Settings):
    mongo_dsn: Sequence[AnyUrl]
    api_layer_api_key: str
    api_layer_base_url: HttpUrl
    source_currencies: list[str]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            RatesService(
                RatesRepository(mongo.rates.rates),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _backup_rates_cron_run(
    app: service.Application[_BackUpCronJobSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    api_layer_client = APILayer(
        app.settings.api_layer_base_url,
        app.settings.api_layer_api_key,
    )

    job = UpdateBackUpRatesJob(
        app.settings.source_currencies,
        BackUpRatesRepository(mongo.backup_rates.backup_rates),
        api_layer_client,
    )

    await job.run()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="rates")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        service.Command(
            name="backup_rates_cron",
            callback=_backup_rates_cron_run,
            settings_class=_BackUpCronJobSettings,
        ),
    )
