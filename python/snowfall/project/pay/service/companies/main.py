import ipaddress
import random
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.pay.service.companies import grpc, repositories
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: service.AsyncApplication[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.CompaniesService(
                companies=repositories.CompaniesRepository(
                    mongo.companies.companies,
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="companies")

    entrypoint.enter_with_commands(
        service.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
    )
