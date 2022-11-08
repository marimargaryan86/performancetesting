import asyncio
import ipaddress
import random
from typing import Sequence

import aiofiles
from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.junction.service.places import cities
from snowfall.project.junction.service.places.grpc import (
    LocationsService,
    PlacesService,
)
from snowfall.project.junction.service.places.places import (
    LocationRepository,
    PlaceRepository,
)
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.grpc.client import create_channel


class _CitiesSettings(service.Settings):
    geodata_address: Sequence[str]
    mongo_dsn: Sequence[AnyUrl]


class _GrpcSettings(service.Settings):
    default_page_size: int = 100
    geodata_address: Sequence[str]
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]


async def _generate_cities(app: service.Application[_CitiesSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(
        create_channel(
            random.choice(app.settings.geodata_address),  # nosec
        ),
    )
    locations_repository = LocationRepository(mongo.places.locations)
    places_repository = PlaceRepository(
        geocoding=geocoding_service,
        collection=mongo.places.places,
    )
    csv_path = filesystem.resource_path(
        "snowfall.project.junction.service.places.main",
        "cities.csv",
    )

    async with aiofiles.open(csv_path) as csv_file:
        resources = []

        async for city in cities.parse_csv(locations_repository, csv_file):
            resources.append(city)

            if len(resources) == 10:
                await asyncio.gather(
                    *[places_repository.create(city) for city in resources],
                )
                resources = []

        if not resources:
            await asyncio.gather(
                *[places_repository.create(resource) for resource in resources],
            )


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(
        create_channel(
            random.choice(app.settings.geodata_address),  # nosec
        ),
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            PlacesService(
                PlaceRepository(
                    geocoding=geocoding_service,
                    collection=mongo.places.places,
                ),
                app.settings.default_page_size,
            ),
            LocationsService(
                LocationRepository(mongo.places.locations),
                app.settings.default_page_size,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="places")

    entrypoint.enter_with_commands(
        service.Command(
            name="generate-cities",
            callback=_generate_cities,
            settings_class=_CitiesSettings,
        ),
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
