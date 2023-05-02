import ipaddress
import random
from typing import Sequence

from pydantic import AnyUrl

from snowfall.project.pay.adapter import rates
from snowfall.project.pay.service.currencies.grpc import CurrencyService
from snowfall.project.pay.service.rates.v1alpha import rates_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.grpc.client import create_channel


class _Settings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    rates_address: Sequence[str]


async def _main(app: service.Application[_Settings]) -> None:
    rates_channel = create_channel(
        random.choice(app.settings.rates_address),  # nosec
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CurrencyService(
                rates.GrpcClient(
                    rates_pb2_grpc.RatesServiceStub(rates_channel),
                ),
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
