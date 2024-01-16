import ipaddress
import random
from collections.abc import Sequence

import httpx
from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.junction.go.adapter import orders
from snowfall.project.junction.go.service.orders.v1 import orders_pb2_grpc
from snowfall.project.pay.adapter import bills as bills_adapter
from snowfall.project.pay.adapter import credit_card_payment as credit_card_adapter
from snowfall.project.pay.adapter import transactions as transactions_adapter
from snowfall.project.pay.service.payments.v1 import credit_card_pb2_grpc
from snowfall.project.pay.service.refunds import grpc, repositories
from snowfall.project.pay.service.transactions.v1 import (
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
    orders_address: str
    cc_login: str
    cc_api_key: str
    cc_address: str
    credit_card_address: str


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    transactions_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.transactions_address,
    )
    orders_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.orders_address,
    )
    credit_card_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.credit_card_address,
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
                orders_client=orders.GrpcClient(
                    orders_pb2_grpc.OrderServiceStub(orders_channel),
                ),
                credit_cards_client=credit_card_adapter.GrpcClient(
                    credit_card_pb2_grpc.CreditCardPaymentServiceStub(
                        credit_card_channel,
                    ),
                ),
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
