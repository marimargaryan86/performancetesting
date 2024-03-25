import asyncio
import ipaddress
import json
import pathlib
import pkgutil
from collections.abc import AsyncIterable, Mapping, Sequence
from typing import Any

import aiocsv
import aiofiles
from pydantic import MongoDsn

from snowfall.project.junction.rocket.service.places import constants
from snowfall.project.junction.rocket.service.places.grpc import PlacesService
from snowfall.project.junction.rocket.service.places.places import (
    PlaceRepository,
    cities_to_places,
    osm_nodes_to_places,
    tag_all_non_cities_against_a_city,
)
from snowfall.project.junction.rocket.service.places.typing import ProviderTypedDict
from snowfall.project.junction.rocket.service.places.v1alpha import models_pb2
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory, mongo_factory
from snowfall.stdlib.transport.grpc import server

_logger = stdout.get_logger()


class _GeneratePlacesSettings(application.Settings):
    geodata_address: str
    mongo_dsn: MongoDsn


class _GrpcSettings(application.Settings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 51055
    mongo_dsn: MongoDsn


async def _generate_places(  # noqa: WPS231
    app: application.Application[_GeneratePlacesSettings],
) -> None:
    asyncio.get_running_loop().slow_callback_duration = 1

    mongo = await mongo_factory.make_database(app=app, dsn=app.settings.mongo_dsn)

    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(
        await grpc_factory.make_insecure_channel(app, app.settings.geodata_address),
    )

    nodes_json = pkgutil.get_data(
        "snowfall.project.junction.rocket.service.places.main",
        "nodes.json",
    )

    if nodes_json is None:
        raise RuntimeError("No nodes.json file present")
    nodes = json.loads(nodes_json.decode("utf-8"))

    country_codes_to_countries_json = pkgutil.get_data(
        "snowfall.project.junction.rocket.service.places.main",
        "country_codes_to_countries.json",
    )

    if country_codes_to_countries_json is None:
        raise RuntimeError("No country_codes_to_countries.json file present")
    country_codes_to_countries = json.loads(
        country_codes_to_countries_json.decode("utf-8"),
    )

    benerail_json = pkgutil.get_data(
        "snowfall.project.junction.rocket.service.places.main",
        "benerail_stations.json",
    )

    df_json = pkgutil.get_data(
        "snowfall.project.junction.rocket.service.places.main",
        "ports.json",
    )

    cities_csv_path = filesystem.resource_path(
        "snowfall.project.junction.rocket.service.places.main",
        "cities_with_iatas_and_benerail_ids.csv",
    )

    provider_json: ProviderTypedDict = {
        models_pb2.TYPE_RAILWAY_STATION: {
            constants.BENERAIL_ID: (
                json.loads(
                    benerail_json.decode("utf-8"),
                )
                if benerail_json
                else []
            ),
        },
        models_pb2.TYPE_FERRY_PORT: {
            constants.DF_ID: json.loads(df_json.decode("utf-8")) if df_json else [],
        },
    }

    places_repo = PlaceRepository(collection=mongo.places.places)

    await _generate_places_from_nodes_and_cities(
        country_codes_to_countries=country_codes_to_countries,
        geocoding_service=geocoding_service,
        nodes=nodes,
        places_repo=places_repo,
        provider_json=provider_json,
        cities_csv_path=cities_csv_path,
    )


async def cities_iterator(csv_path: pathlib.Path) -> AsyncIterable[Mapping[str, str]]:
    async with aiofiles.open(csv_path) as cities_csv:
        async for city_dict in aiocsv.AsyncDictReader(cities_csv):
            yield city_dict


async def _generate_places_from_nodes_and_cities(
    country_codes_to_countries: Mapping[str, str],
    geocoding_service: geocoding_pb2_grpc.GeocodingServiceStub,
    nodes: Sequence[Mapping[str, Any]],
    places_repo: PlaceRepository,
    provider_json: ProviderTypedDict,
    cities_csv_path: pathlib.Path,
) -> None:
    async for place in osm_nodes_to_places(  # noqa: WPS352
        osm_nodes=nodes,
        provider_jsons=provider_json,
        geocoding=geocoding_service,
        country_codes_to_countries=country_codes_to_countries,
    ):
        try:
            await places_repo.insert(place)
        except Exception:
            _logger.exception("Issue storing place", place_source_id=place.source_id)

    async for city in cities_to_places(  # noqa: WPS352
        cities=cities_iterator(cities_csv_path),
        places_repository=places_repo,
        geocoding=geocoding_service,
        country_codes_to_countries=country_codes_to_countries,
    ):
        try:
            await places_repo.insert(city)
        except Exception:
            _logger.exception("Issue storing city place", city_source_id=city.source_id)

    await tag_all_non_cities_against_a_city(places_repository=places_repo)


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = await mongo_factory.make_database(app=app, dsn=app.settings.mongo_dsn)
    grpc_server = server.create_server(
        address=app.settings.grpc_address,
        port=app.settings.grpc_port,
        services=[
            PlacesService(
                places_repository=PlaceRepository(
                    collection=mongo.places.places,
                ),
                default_page_size=app.settings.default_page_size,
            ),
        ],
    )
    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="places")

    entrypoint.enter_with_commands(
        application.Command(
            name="generate-places",
            callback=_generate_places,
            settings_class=_GeneratePlacesSettings,
        ),
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
