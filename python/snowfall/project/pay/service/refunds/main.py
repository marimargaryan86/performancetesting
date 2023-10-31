import ipaddress
import random
from collections.abc import Sequence

import httpx
from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.adapter import bills as bills_adapter
from snowfall.project.pay.adapter import transactions as transactions_adapter
from snowfall.project.pay.service.refunds import grpc, repositories
from snowfall.project.pay.service.transactions.v1alpha import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.stdlib.instrumentation.httpx import metrics
from snowfall.stdlib.service import application, grpc_factory
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    transactions_address: str
    cc_login: str
    cc_api_key: str
    cc_address: str
    stripe_api_key: str


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    transactions_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.transactions_address,
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.RefundsService(
                refunds=repositories.RefundsRepository(
                    mongo.refunds.refunds,
                ),
                transactions_client=transactions_adapter.GrpcClient(
                    transactions_pb2_grpc.TransactionsServiceStub(
                        transactions_channel,
                    ),
                ),
                bills_client=bills_adapter.GrpcClient(
                    transactions_pb2_grpc.BillsServiceStub(
                        transactions_channel,
                    ),
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
                stripe_api_key=app.settings.stripe_api_key,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="refunds")

    entrypoint.enter_with_commands(
        application.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
    )
