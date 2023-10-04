import ipaddress

import boto3
import pydantic
import shapefile

from snowfall.service.geodata import geocoding, reverse_geocoding
from snowfall.service.geodata.grpc import GeocodingService
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application, redis_factory
from snowfall.stdlib.transport.grpc import server


class _Settings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: application.NetworkPort = 50051
    redis_dsn: pydantic.RedisDsn
    aws_default_region: str
    aws_access_key_id: str
    aws_secret_access_key: pydantic.SecretStr


async def _main(app: application.Application[_Settings]) -> None:
    shp_path = filesystem.resource_path(
        "snowfall.service.geodata.main",
        "EEZ_land_union_v3_202003.zip",
    )
    shp_file = shapefile.Reader(shp_path)
    redis_conn = await redis_factory.make_connection(
        app,
        app.settings.redis_dsn,
        decode_responses=True,
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            GeocodingService(
                redis.Client(redis_conn),
                geocoder=geocoding.Geocoder(
                    shp_file,
                    app.user_agent,
                ),
                reverse_geocoder=reverse_geocoding.ReverseGeocoder(
                    boto3.client("location"),
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="geodata")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_main,
            settings_class=_Settings,
        ),
    )
