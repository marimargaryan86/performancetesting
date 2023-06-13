import datetime
import ipaddress
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.service.authentication import auth, repository
from snowfall.service.authentication.grpc import AuthenticationService
from snowfall.stdlib import service
from snowfall.stdlib.format import jwt
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    default_page_size: int = 100
    jwt_private_key: str
    jwt_public_key: str
    jwt_ttl: datetime.timedelta = datetime.timedelta(hours=1)
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
                auth.JWTFactory(
                    ttl=app.settings.jwt_ttl,
                ),
                jwt_encoder=jwt.Encoder(
                    private_key=app.settings.jwt_private_key,
                    algorithm="RS256",
                ),
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
