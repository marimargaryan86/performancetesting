import ipaddress

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.service.accounts.grpc import (
    AccountsRepository,
    AccountsService,
)
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: AnyUrl


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        app.settings.mongo_dsn,
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            AccountsService(
                AccountsRepository(mongo.accounts.accounts),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="accounts")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
