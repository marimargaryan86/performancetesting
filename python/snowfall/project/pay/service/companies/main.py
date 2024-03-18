import ipaddress
import random
from collections.abc import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.adapter import invoice_payment
from snowfall.project.pay.service.companies import grpc, repositories
from snowfall.project.pay.service.payments.v1 import (
    invoice_pb2_grpc,
)
from snowfall.stdlib import money
from snowfall.stdlib.service import application, grpc_factory
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    currencies_address: str
    payments_address: str
    cc_login: str
    cc_api_key: str
    cc_address: str
    currencies: Sequence[money.Currency]


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.CompaniesService(
                companies=repositories.CompaniesRepository(
                    mongo.companies.companies,
                ),
                invoice_client=invoice_payment.GrpcClient(
                    invoice_pb2_grpc.InvoiceServiceStub(
                        await grpc_factory.make_insecure_channel(
                            app,
                            app.settings.payments_address,
                        ),
                    ),
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="companies")

    entrypoint.enter_with_commands(
        application.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
    )
