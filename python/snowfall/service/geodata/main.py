import ipaddress
import random
from collections.abc import Sequence

import shapefile
from pydantic import AnyUrl
from redis import asyncio as aioredis

from snowfall.service.geodata import geocoding
from snowfall.service.geodata.grpc import GeocodingService
from snowfall.stdlib import service
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.grpc import server


class _Settings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    redis_dsn: Sequence[AnyUrl]


async def _main(app: service.Application[_Settings]) -> None:
    shp_path = filesystem.resource_path(
        "snowfall.service.geodata.main",
        "EEZ_land_union_v3_202003.zip",
    )
    shp_file = shapefile.Reader(shp_path)

    async with aioredis.from_url(
        random.choice(app.settings.redis_dsn),  # nosec
        decode_responses=True,
    ).client() as redis_conn:
        grpc_server = server.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            [
                GeocodingService(
                    redis.Client(redis_conn),
                    geocoder=geocoding.ReverseGeocoder(shp_file, app.user_agent),
                ),
            ],
        )

        async with grpc_server.serve() as running:
            await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="geodata")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_main,
            settings_class=_Settings,
        ),
    )
