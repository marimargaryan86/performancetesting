import ipaddress
import random
from collections.abc import Sequence

import httpx
from motor import motor_asyncio
from pydantic import AnyUrl, RedisDsn

from snowfall.project.pay.service.rates import cache
from snowfall.project.pay.service.rates.backup_rates_cron import UpdateBackUpRatesJob
from snowfall.project.pay.service.rates.grpc import RatesService
from snowfall.project.pay.service.rates.rates import BackUpRatesRepository
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.service import application, redis_factory
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: RedisDsn


class _BackUpCronJobSettings(application.Settings):
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: RedisDsn
    cc_login: str
    cc_api_key: str
    cc_address: str
    currencies: Sequence[str]


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=True,
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            RatesService(
                BackUpRatesRepository(mongo.backup_rates.backup_rates),
                cache.RateRepository(redis_client),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _backup_rates_cron_run(
    app: application.Application[_BackUpCronJobSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=True,
    )

    job = UpdateBackUpRatesJob(
        BackUpRatesRepository(mongo.backup_rates.backup_rates),
        PaymentClient(
            base_url=app.settings.cc_address,
            auth=CurrencyCloudAuth(
                base_url=app.settings.cc_address,
                login_id=app.settings.cc_login,
                api_key=app.settings.cc_api_key,
            ),
            client=metrics.register(httpx.AsyncClient()),
        ),
        app.settings.currencies,
        cache.RateRepository(redis_client, 1),
    )

    await job.run()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="rates")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        application.Command(
            name="backup-rates-cron",
            callback=_backup_rates_cron_run,
            settings_class=_BackUpCronJobSettings,
        ),
    )
