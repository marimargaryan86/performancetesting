import ipaddress
import random
from collections.abc import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.pay.service.payers.grpc import PayerService
from snowfall.project.pay.service.payers.payers import PayersRepository
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(service.Settings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
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
    entrypoint = service.Entrypoint(name="payers")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
