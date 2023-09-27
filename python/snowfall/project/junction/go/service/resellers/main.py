import ipaddress
import random
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.junction.go.service.resellers import resellers_repository
from snowfall.project.junction.go.service.resellers.grpc import ResellerService
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server as grpc_server


class _ServeSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    default_page_size: int = 100
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: application.AsyncApplication[_ServeSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            ResellerService(
                resellers_repo=resellers_repository.ResellerRepository(
                    collection=mongo.resellers.resellers,
                ),
                default_page_size=app.settings.default_page_size,
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
