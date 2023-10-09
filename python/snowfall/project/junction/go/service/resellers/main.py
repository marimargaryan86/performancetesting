import ipaddress
import random
from collections.abc import Sequence

import httpx
import pydantic
from motor import motor_asyncio

from snowfall.project.junction.go.service.resellers import persistence
from snowfall.project.junction.go.service.resellers.grpc import ResellerService
from snowfall.project.pay.adapter import companies as companies_adapter
from snowfall.project.pay.adapter import currencies as currencies_adapter
from snowfall.project.pay.service.companies.v1alpha import (
    grpc_pb2_grpc as companies_grpc,
)
from snowfall.project.pay.service.currencies.v1alpha import currencies_pb2_grpc
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc.client import create_channel
from snowfall.vendor.consul.client import ConsulClient


class _ServeSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    default_page_size: int = 100
    mongo_dsn: Sequence[pydantic.AnyUrl]
    consul_api_base_url: pydantic.AnyUrl
    consul_api_token: str
    consul_api_version: str = "v1"
    companies_address: str
    currencies_address: str


async def _serve(app: application.Application[_ServeSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    http_client = await app.stack.enter_async_context(httpx.AsyncClient())

    consul_client = ConsulClient(
        api_base_url=str(app.settings.consul_api_base_url),
        api_token=app.settings.consul_api_token,
        version=app.settings.consul_api_version,
        httpx_client=http_client,
    )

    companies_channel = create_channel(
        app.settings.companies_address,
    )

    company_client = companies_adapter.GrpcClient(
        companies_grpc.CompaniesServiceStub(
            companies_channel,
        ),
    )

    currencies_channel = create_channel(
        app.settings.currencies_address,
    )
    currency_client = currencies_adapter.GrpcClient(
        currencies_pb2_grpc.CurrencyServiceStub(
            currencies_channel,
        ),
    )

    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            ResellerService(
                resellers_repo=persistence.ResellerRepository(
                    collection=mongo.resellers.resellers,
                ),
                default_page_size=app.settings.default_page_size,
                consul_client=consul_client,
                environment=app.environment,
                company_client=company_client,
                currency_client=currency_client,
            ),
        ],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="resellers")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_ServeSettings,
        ),
    )
