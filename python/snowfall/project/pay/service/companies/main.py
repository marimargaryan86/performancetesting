import ipaddress
import random
from collections.abc import Sequence

import httpx
from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.companies import cron_jobs, grpc, repositories
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.stdlib import money
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    currencies_address: str
    cc_login: str
    cc_api_key: str
    cc_address: str
    currencies: Sequence[money.Currency]


class _AccountSyncSettings(application.Settings):
    mongo_dsn: AnyUrl
    cc_login: str
    cc_api_key: str
    cc_address: str


async def _serve(app: application.AsyncApplication[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    payment_client = PaymentClient(
        base_url=app.settings.cc_address,
        auth=CurrencyCloudAuth(
            base_url=app.settings.cc_address,
            login_id=app.settings.cc_login,
            api_key=app.settings.cc_api_key,
        ),
        client=metrics.register(httpx.AsyncClient()),
    )

    currencies_channel = create_channel(
        app.settings.currencies_address,
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.CompaniesService(
                companies=repositories.CompaniesRepository(
                    mongo.companies.companies,
                ),
            ),
            grpc.LeadCompaniesService(
                lead_companies=repositories.LeadCompaniesRepository(
                    mongo.companies.lead_companies,
                ),
            ),
            grpc.AccountsService(
                accounts=repositories.AccountsRepository(mongo.companies.accounts),
                payment_client=payment_client,
            ),
            grpc.ContactsService(
                contacts=repositories.ContactsRepository(mongo.companies.contacts),
                companies=repositories.CompaniesRepository(
                    mongo.companies.companies,
                ),
            ),
            grpc.BeneficiariesService(
                beneficiaries=repositories.BeneficiaryRepository(
                    mongo.companies.beneficiaries,
                ),
                companies=repositories.CompaniesRepository(
                    mongo.companies.companies,
                ),
                accounts=repositories.AccountsRepository(mongo.companies.accounts),
                currencies_client=currencies.GrpcClient(
                    currencies_pb2_grpc.CurrencyServiceStub(
                        currencies_channel,
                    ),
                ),
                payment_client=payment_client,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _sync_accounts_cron_run(
    app: application.Application[_AccountSyncSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(str(app.settings.mongo_dsn))
    payment_client = PaymentClient(
        base_url=app.settings.cc_address,
        auth=CurrencyCloudAuth(
            base_url=app.settings.cc_address,
            login_id=app.settings.cc_login,
            api_key=app.settings.cc_api_key,
        ),
        client=metrics.register(httpx.AsyncClient()),
    )
    sync_account = cron_jobs.SyncAccounts(
        payment_client,
        repositories.AccountsRepository(mongo.companies.accounts),
    )
    await sync_account.sync_accounts()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="companies")

    entrypoint.enter_with_commands(
        application.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
        application.Command(
            name="sync_accounts",
            callback=_sync_accounts_cron_run,
            settings_class=_AccountSyncSettings,
        ),
    )
