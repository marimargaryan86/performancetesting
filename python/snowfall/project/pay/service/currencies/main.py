import ipaddress
from collections.abc import Sequence

from pydantic import AnyUrl

from snowfall.project.pay.adapter import rates
from snowfall.project.pay.service.currencies.grpc import CurrencyService
from snowfall.project.pay.service.currencies.repositories import CurrencyRepository
from snowfall.project.pay.service.rates.v1alpha import rates_pb2_grpc
from snowfall.stdlib import money
from snowfall.stdlib.service import application, grpc_factory
from snowfall.stdlib.transport.grpc import server


class _Settings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    rates_address: str
    currencies: Sequence[money.Currency]


async def _main(app: application.Application[_Settings]) -> None:
    rates_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.rates_address,
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CurrencyService(
                rates.GrpcClient(
                    rates_pb2_grpc.RatesServiceStub(rates_channel),
                ),
                CurrencyRepository(
                    app.settings.currencies,
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="currencies")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_main,
            settings_class=_Settings,
        ),
    )
