import ipaddress
from typing import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.service.authentication import repository
from snowfall.service.authentication.grpc import AuthenticationService
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50063
    default_page_size: int = 100
    jwt_private_key: str
    jwt_public_key: str
    jwt_token_version: str
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(app.settings.mongo_dsn)

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            AuthenticationService(
                repository.UsersRepository(
                    collection=mongo.authentication.users,
                ),
                default_page_size=app.settings.default_page_size,
                private_key_content=app.settings.jwt_private_key,
                jwt_token_version=app.settings.jwt_token_version,
            ),
        ],
    )

    async with grpc_server.serve() as runner:
        await runner.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="authentication")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
