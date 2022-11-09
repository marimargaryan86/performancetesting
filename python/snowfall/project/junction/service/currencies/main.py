import datetime
import ipaddress

from pydantic import HttpUrl

from snowfall.project.junction.service.currencies.grpc import CurrencyService
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.bound.client import Bound


class _Settings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    base_url: HttpUrl
    email: str
    password: str
    bound_api_timeout: datetime.timedelta = datetime.timedelta(seconds=15)


async def _main(app: service.Application[_Settings]) -> None:
    bound_client = Bound(
        app.settings.base_url,
        app.settings.email,
        app.settings.password,
        app.settings.bound_api_timeout.total_seconds(),
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CurrencyService(
                bound_client,
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
