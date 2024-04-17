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

from snowfall.project.junction.go.service.places import (
    cities,
    constant,
    locations,
    places,
)
from snowfall.project.junction.go.service.places.grpc import (
    LocationsService,
    PlacesService,
)
from snowfall.project.junction.go.service.places.typing import ProviderTypedDict
from snowfall.project.junction.go.service.places.v1 import models_pb2
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


async def _generate_cities(app: application.Application[_CitiesSettings]) -> None:  # noqa: WPS231
    # As a script, we don't need to worry about blocking the event loop.
    asyncio.get_running_loop().slow_callback_duration = 1
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

    benerail_json = pkgutil.get_data(
        "snowfall.project.junction.go.service.places.main",
        "benerail_stations.json",
    )

    sat_json = pkgutil.get_data(
        "snowfall.project.junction.go.service.places.main",
        "train_stations.json",
    )

    ask2go_json = pkgutil.get_data(
        "snowfall.project.junction.go.service.places.main",
        "ask2go_stations.json",
    )
    ask2go_list = json.loads(ask2go_json.decode("utf-8")) if ask2go_json else []
    df_json = pkgutil.get_data(
        "snowfall.project.junction.go.service.places.main",
        "ports.json",
    )

    dbs_json = pkgutil.get_data(
        "snowfall.project.junction.go.service.places.main",
        "distribusion.json",
    )

    provider_json: ProviderTypedDict = {
        models_pb2.Location.TYPE_RAILWAY_STATION: {
            constant.BENERAIL_ID: (
                json.loads(
                    benerail_json.decode("utf-8"),
                )
                if benerail_json
                else []
            ),
            constant.SAT_ID: json.loads(sat_json.decode("utf-8")) if sat_json else [],
            constant.ASK2GO_ID: [
                {
                    "id": item["identifier"],
                    "name": item["name"],
                    "time_zone": item["timezone"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                }
                for item in ask2go_list
            ],
        },
        models_pb2.Location.TYPE_FERRY_PORT: {
            constant.DF_ID: json.loads(df_json.decode("utf-8")) if df_json else [],
        },
        models_pb2.Location.TYPE_BUS_STATION: {
            constant.DBS_ID: json.loads(dbs_json.decode("utf-8")) if dbs_json else [],
        },
    }

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
            async for city in cities.parse_csv(locations_repo, csv_file, provider_json):
                count += 1
                cache = places_cache.get(city.location.id)
                if cache:
                    # Restore geodata from cache in order to skip it in create().
                    city.location.country_code = cache["location"]["country_code"]
                    city.location.time_zone = cache["location"]["time_zone"]

                tg.create_task(  # type: ignore[unused-awaitable]
                    places.create(
                        places_repository,
                        city,
                        sem,
                        count,
                    ),
                )

        async for node in locations.node_to_place(locations_repo, nodes, provider_json):
            count += 1
            cache = places_cache.get(node.location.id)
            if cache:
                # Restore geodata from cache in order to skip it in create().
                node.location.country_code = cache["location"]["country_code"]
                node.location.time_zone = cache["location"]["time_zone"]

            tg.create_task(  # type: ignore[unused-awaitable]
                places.create(
                    places_repository,
                    node,
                    sem,
                    count,
                ),
            )

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
    entrypoint = application.Entrypoint(name="junction-go-places")

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
