import datetime
import ipaddress
import random
from collections.abc import Sequence

import httpx
import pydantic
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.pay.adapter import companies, currencies
from snowfall.project.pay.service.companies.v1alpha import (
    grpc_pb2_grpc as companies_grpc_pb2,
)
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.project.pay.service.transactions import cache, transactions
from snowfall.project.pay.service.transactions.grpc import (
    BillsService,
    ConversionsService,
    QuotationsService,
    TransactionsService,
)
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    redis_dsn: Sequence[pydantic.AnyUrl]
    currencies_address: str
    companies_address: str
    cc_login: str
    cc_api_key: str
    cc_address: str


async def _serve(app: application.AsyncApplication[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    redis_conn = await app.stack.enter_async_context(
        aioredis.from_url(
            str(random.choice(app.settings.redis_dsn)),  # noqa: S311
            decode_responses=True,
            retry_on_error=[aioredis.ConnectionError],
        ).client(),
    )
    redis_client = redis.Client[str](
        redis_conn,
        prefix=app.name,
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            TransactionsService(
                transactions=transactions.TransactionsRepository(
                    mongo.transactions.transactions,
                ),
                conversions=transactions.ConversionsRepository(
                    mongo.transactions.conversions,
                ),
                bills=transactions.BillsRepository(
                    mongo.transactions.bills,
                ),
                payment_client=PaymentClient(
                    base_url=app.settings.cc_address,
                    auth=CurrencyCloudAuth(
                        base_url=app.settings.cc_address,
                        login_id=app.settings.cc_login,
                        api_key=app.settings.cc_api_key,
                    ),
                    client=metrics.register(httpx.AsyncClient()),
                ),
                companies_client=companies.GrpcClient(
                    companies_grpc_pb2.CompaniesServiceStub(
                        create_channel(app.settings.companies_address),
                    ),
                ),
            ),
            QuotationsService(
                quotations=transactions.QuotationsRepository(
                    mongo.transactions.quotations,
                ),
                user_sessions=cache.UserSessionRepository(
                    redis_client=redis_client,
                    cache_ttl=datetime.timedelta(minutes=15),
                ),
                currencies_client=currencies.GrpcClient(
                    currencies_pb2_grpc.CurrencyServiceStub(
                        create_channel(app.settings.currencies_address),
                    ),
                ),
            ),
            ConversionsService(
                conversions=transactions.ConversionsRepository(
                    mongo.transactions.conversions,
                ),
            ),
            BillsService(
                bills=transactions.BillsRepository(
                    mongo.transactions.bills,
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="transactions")

    entrypoint.enter_with_commands(
        application.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
    )
