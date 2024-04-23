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
from snowfall.stdlib.service import application, grpc_factory, httpx_factory
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.consul.client import ConsulClient


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    currencies_address: str
    payments_address: str
    consul_api_base_url: AnyUrl
    consul_api_token: str
    consul_api_version: str = "v1"
    currencies: Sequence[money.Currency]


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    http_client = await httpx_factory.make_client(app)

    consul_client = ConsulClient(
        api_base_url=str(app.settings.consul_api_base_url),
        api_token=app.settings.consul_api_token,
        version=app.settings.consul_api_version,
        httpx_client=http_client,
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
                consul_client=consul_client,
            ),
            grpc.ContactsService(
                contacts=repositories.ContactsRepository(mongo.companies.contacts),
                companies=repositories.CompaniesRepository(
                    mongo.companies.companies,
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="pay-companies")

    entrypoint.enter_with_commands(
        application.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
    )
