import asyncio
import ipaddress
import json
import logging
import pathlib
import pkgutil
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
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory
from snowfall.stdlib.transport.grpc import server


class _CitiesSettings(application.Settings):
    geodata_address: str
    mongo_dsn: Sequence[AnyUrl]
    places_dump: pathlib.Path


class _GrpcSettings(application.Settings):
    default_page_size: int = 100
    geodata_address: str
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]


async def _generate_cities(app: application.Application[_CitiesSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(
        await grpc_factory.make_insecure_channel(app, app.settings.geodata_address),
    )

    cities_csv_path = filesystem.resource_path(
        "snowfall.project.junction.go.service.places.main",
        "cities.csv",
    )

    places_repository = places.PlaceRepository(
        geocoding=geocoding_service,
        collection=mongo.places.places,
    )
    nodes_json = pkgutil.get_data(
        "snowfall.project.junction.go.service.places.main",
        "nodes.json",
    )

    filesystem.resource_path(
        "snowfall.project.junction.go.service.places.main",
        "cities.csv",
    )

    if nodes_json is None:
        raise RuntimeError(
            "No nodes file to build places from",
        )

    nodes = json.loads(nodes_json.decode("utf-8"))

    bson_content = app.settings.places_dump.read_bytes()

    places_dump: list[dict[str, Any]] = bson.decode_all(bson_content)
    places_collection = mongo.places.places
    places_cache = {place["_id"]: place for place in places_dump}
    locations_repo = places.LocationRepository(mongo.places.locations)
    sem = asyncio.Semaphore(100)
    count = 1
    async with asyncio.TaskGroup() as tg:
        async with aiofiles.open(cities_csv_path) as csv_file:
            async for city in cities.parse_csv(locations_repo, csv_file):
                count += 1
                cache = places_cache.get(city.location.id)
                if cache:
                    # Restore geodata from cache in order to skip it in create().
                    city.location.country_code = cache["location"]["country_code"]
                    city.location.time_zone = cache["location"]["time_zone"]

                tg.create_task(places.create(places_repository, city, sem, count))  # type: ignore[unused-awaitable]

        async for node in locations.node_to_place(locations_repo, nodes):
            count += 1
            cache = places_cache.get(node.location.id)
            if cache:
                # Restore geodata from cache in order to skip it in create().
                node.location.country_code = cache["location"]["country_code"]
                node.location.time_zone = cache["location"]["time_zone"]

            tg.create_task(places.create(places_repository, node, sem, count))  # type: ignore[unused-awaitable]

    logging.info("Generate places completed.")
    places_count = await places_collection.count_documents({})
    if places_count < 10000:
        raise RuntimeError(
            "Failed to export places (found {0})".format(places_count),
        )


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(
        await grpc_factory.make_insecure_channel(app, app.settings.geodata_address),
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
    entrypoint = application.Entrypoint(name="places")

    entrypoint.enter_with_commands(
        application.Command(
            name="generate-cities",
            callback=_generate_cities,
            settings_class=_CitiesSettings,
        ),
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
