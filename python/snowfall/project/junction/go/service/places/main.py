import asyncio
import ipaddress
import pathlib
import random
from collections.abc import Sequence
from typing import Any

import aiofiles
import bson
from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.junction.go.service.places import cities, locations, places
from snowfall.project.junction.go.service.places.grpc import (
    LocationsService,
    PlacesService,
)
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.grpc.client import create_channel


class _CitiesSettings(service.Settings):
    geodata_address: str
    mongo_dsn: Sequence[AnyUrl]
    places_dump: pathlib.Path


class _GrpcSettings(service.Settings):
    default_page_size: int = 100
    geodata_address: str
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]


async def _generate_cities(app: service.Application[_CitiesSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # noqa: S311
    )
    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(
        create_channel(app.settings.geodata_address),
    )
    places_repository = places.PlaceRepository(
        geocoding=geocoding_service,
        collection=mongo.places.places,
    )
    csv_path = filesystem.resource_path(
        "snowfall.project.junction.go.service.places.main",
        "cities.csv",
    )

    bson_content = app.settings.places_dump.read_bytes()
    places_dump: list[Any] = bson.decode_all(bson_content) if bson_content else []
    locations_collection = mongo.places.locations
    nodes_collection = mongo.places.nodes
    places_collection = mongo.places.places
    places_cache = {place["_id"]: place for place in places_dump}
    locations_repo = places.LocationRepository(locations_collection)
    sem = asyncio.Semaphore(100)
    count = 1

    async with asyncio.TaskGroup() as tg:
        async for node in locations.node_to_place(locations_repo, nodes_collection):
            count += 1
            place = places_cache.get(node.location.id)
            task = (
                places.replace_one(
                    places_collection,
                    place,
                    count,
                )
                if place
                else places.create(
                    places_repository,
                    node,
                    sem,
                    count,
                )
            )

            tg.create_task(task)  # type: ignore[unused-awaitable]

        async with aiofiles.open(csv_path) as csv_file:
            async for city in cities.parse_csv(locations_repo, csv_file):
                count += 1
                place = places_cache.get(city.location.id)
                task = (
                    places.replace_one(
                        places_collection,
                        place,
                        count,
                    )
                    if place
                    else places.create(
                        places_repository,
                        city,
                        sem,
                        count,
                    )
                )
                tg.create_task(task)  # type: ignore[unused-awaitable]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # noqa: S311
    )
    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(
        create_channel(app.settings.geodata_address),
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            PlacesService(
                places.PlaceRepository(
                    geocoding=geocoding_service,
                    collection=mongo.places.places,
                ),
                app.settings.default_page_size,
            ),
            LocationsService(
                places.LocationRepository(mongo.places.locations),
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
