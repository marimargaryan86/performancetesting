import ipaddress
import uuid

import pydantic

from snowfall.project.junction.content import meta
from snowfall.project.junction.content import trips as provider_trips
from snowfall.project.junction.content.service.duffel import trips
from snowfall.stdlib.service import application, grpc_factory, httpx_factory
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.duffel import client
from snowfall.vendor.rate_limiter import client as rate_limiter
from snowfall.vendor.rate_limiter import config, gubernator_pb2_grpc

_PROVIDER_ID = uuid.UUID("5d18e8e1-48e3-4b7c-82b9-62bd97a92f91")
_PROVIDER_NAME = "Duffel"


class _Settings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_version: str = "v1"
    http_timeout: int = 30
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, config.RateLimitConfig]


async def _serve(app: application.Application[_Settings]) -> None:
    httpx_client = await httpx_factory.make_client(app)
    rate_limit_client = rate_limiter.Client(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["duffel"],
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            meta.MetaService(
                provider_id=_PROVIDER_ID,
                provider_name=_PROVIDER_NAME,
            ),
            provider_trips.TripService(
                one_way=trips.Trips(
                    search_client=client.DuffelClient(
                        http_client=httpx_client,
                        api_base_url=str(app.settings.api_base_url),
                        api_key=app.settings.api_key,
                        version=app.settings.api_version,
                        rate_limit_client=rate_limit_client,
                    ),
                    transformer=trips.Transformer(),
                ).find_one_way,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="mock")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_Settings,
        ),
    )
