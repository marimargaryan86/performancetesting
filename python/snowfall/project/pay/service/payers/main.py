import ipaddress
import random
from collections.abc import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.service.payers.grpc import PayerService
from snowfall.project.pay.service.payers.payers import PayersRepository
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(application.Settings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            PayerService(
                PayersRepository(mongo.payers.payers),
                default_page_size=app.settings.default_page_size,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="payers")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
