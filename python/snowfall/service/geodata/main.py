import ipaddress
import random
from collections.abc import Sequence

import aioredis
from pydantic import AnyUrl

from snowfall.service.geodata import geocoding
from snowfall.service.geodata.grpc import GeocodingService
from snowfall.stdlib import service
from snowfall.stdlib.persistence import redis
from snowfall.stdlib.transport import grpc


class _Settings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    redis_dsn: Sequence[AnyUrl]


async def _main(app: service.Application[_Settings]) -> None:
    async with aioredis.from_url(
        random.choice(app.settings.redis_dsn),  # nosec
        decode_responses=True,
    ).client() as redis_conn:
        grpc_server = grpc.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            [
                GeocodingService(
                    redis.Client(redis_conn),
                    geocoder=geocoding.ReverseGeocoder(app.user_agent),
                ),
            ],
        )

        async with grpc_server.serve() as server:
            await server.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="geodata")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_main,
            settings_class=_Settings,
        ),
    )
