import ipaddress

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.service.accounts import cron_jobs
from snowfall.project.pay.service.accounts.grpc import (
    AccountsRepository,
    AccountsService,
)
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.currency_cloud.client import (
    CurrencyCloudAuth,
    CurrencyCloudConfig,
    PaymentClient,
)


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: AnyUrl


class _SyncSettings(service.Settings):
    mongo_dsn: AnyUrl
    cc_login: str
    cc_api_key: str
    cc_env: str
    cc_address: str


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        app.settings.mongo_dsn,
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            AccountsService(
                AccountsRepository(mongo.accounts.accounts),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _sync_accounts_cron_run(
    app: service.Application[_SyncSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(app.settings.mongo_dsn)
    payment_client = PaymentClient(
        cc_config=CurrencyCloudConfig(
            app.settings.cc_login,
            app.settings.cc_api_key,
            app.settings.cc_env,
        ),
        base_url=app.settings.cc_address,
        auth=CurrencyCloudAuth(
            base_url=app.settings.cc_address,
            login_id=app.settings.cc_login,
            api_key=app.settings.cc_api_key,
        ),
    )
    sync_account = cron_jobs.SyncAccounts(
        payment_client,
        AccountsRepository(mongo.accounts.accounts),
    )
    await sync_account.sync_accounts()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="accounts")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        service.Command(
            name="sync",
            callback=_sync_accounts_cron_run,
            settings_class=_SyncSettings,
        ),
    )
