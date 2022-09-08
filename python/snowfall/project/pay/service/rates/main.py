import ipaddress
import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl, HttpUrl

from snowfall.project.pay.service.rates.grpc import RatesService
from snowfall.project.pay.service.rates.rates import (
    MonitoredRatesRepository,
    RatesRepository,
)
from snowfall.project.pay.service.rates.rates_cron import FetchRateJob
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.bound.client import Bound


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50062
    mongo_dsn: Sequence[AnyUrl]
    bound_base_url: HttpUrl
    bound_email: str
    bound_password: str


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
                MonitoredRatesRepository(mongo.monitored_rates.monitored_rates),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _cron_run(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    bound_client = Bound(
        app.settings.bound_base_url,
        app.settings.bound_email,
        app.settings.bound_password,
    )

    job = FetchRateJob(
        RatesRepository(mongo.rates.rates),
        MonitoredRatesRepository(mongo.monitored_rates.monitored_rates),
        bound_client,
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
            name="cron",
            callback=_cron_run,
            settings_class=_GrpcSettings,
        ),
    )
