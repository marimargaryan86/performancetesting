import datetime
import ipaddress

import pydantic

from snowfall.adapter import authentication
from snowfall.service.authentication import grpc, repository
from snowfall.stdlib.format import jwt
from snowfall.stdlib.service import application, mongo_factory
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.http import auth as stdlib_auth
from snowfall.vendor.ory import client


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: application.NetworkPort = 50051
    default_page_size: pydantic.PositiveInt = 100
    jwt_private_key: pydantic.SecretStr
    jwt_public_key: str
    jwt_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    mongo_dsn: pydantic.MongoDsn
    ory_application_url: pydantic.HttpUrl
    ory_api_key: pydantic.SecretStr


async def _serve(app: application.AsyncApplication[_GrpcSettings]) -> None:
    mongo_db = await mongo_factory.make_database(app, app.settings.mongo_dsn)
    ory_client = client.OryClient(
        base_url=str(app.settings.ory_application_url),
        auth=stdlib_auth.TokenAuth(token=app.settings.ory_api_key.get_secret_value()),
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.AuthenticationService(
                repository.UsersRepository(
                    collection=mongo_db.users,
                ),
                authentication.JWTFactory(
                    ttl=app.settings.jwt_ttl,
                ),
                jwt_encoder=jwt.Encoder(
                    private_key=app.settings.jwt_private_key.get_secret_value(),
                    algorithm="RS256",
                ),
            ),
            grpc.OAuthService(ory_client=ory_client),
            grpc.SessionService(ory_client=ory_client),
        ],
    )

    async with grpc_server.serve() as runner:
        await runner.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="authentication")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
