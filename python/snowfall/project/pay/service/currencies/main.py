import ipaddress
import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.service.currencies.grpc import CurrencyService
from snowfall.project.pay.service.rates.rates import BackUpRatesRepository
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.apilayer.client import APILayer


class _Settings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    api_layer_api_key: str
    api_layer_base_url: str
    mongo_dsn: Sequence[AnyUrl]


async def _main(app: service.Application[_Settings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    api_layer_client = APILayer(
        app.settings.api_layer_base_url,
        app.settings.api_layer_api_key,
        timeout=1.0,
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CurrencyService(
                api_layer_client,
                BackUpRatesRepository(mongo.backup_rates.backup_rates),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="currencies")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_main,
            settings_class=_Settings,
        ),
    )
