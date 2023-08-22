import datetime
import os
from collections.abc import AsyncIterable

import numpy as np
import pandas as pd
from google.protobuf import timestamp_pb2
from motor import motor_asyncio
from pycountry import countries
from unidecode import unidecode

from snowfall.project.junction.extensions.service.mobile_api import (
    bootstrap,
    repository,
)
from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.project.junction.go.service.places.places import PlaceRepository
from snowfall.project.junction.go.service.places.v1 import (
    models_pb2 as places_models_pb2,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import latlng_pb2

_SERVICE_NAME = "mobile-api"
_ATTRIBUTES_KEY = "attributes"

_CITY_RADIUS_M = int(
    os.getenv("_CITY_RADIUS_M", "50000"),  # noqa: WPS432
)


async def migrate(settings: bootstrap.MigrateSettings) -> None:  # noqa: WPS210, WPS217
    mongo = motor_asyncio.AsyncIOMotorClient(settings.mongo_dsn)
    places_repository = repository.PlacesRepository(mongo[settings.mongo_db]["places"])
    osm_data = pd.read_csv(
        filesystem.resource_path(
            "snowfall.project.junction.extensions.service.mobile_api.main",
            "cities_populations.csv",
        ),
        sep=";",
        engine="python",
        encoding="utf8",
        on_bad_lines="skip",
    )

    go_repo = PlaceRepository(geocoding=None, collection=mongo.places.places)

    ids_from_go = await go_repo.get_ids()
    existing_ids = await places_repository.get_ids()
    to_add = ids_from_go - existing_ids
    to_remove = existing_ids - ids_from_go

    places_to_add = await go_repo.get_by_ids(to_add)
    await _save_enrich_data(places_to_add, places_repository, osm_data)
    await places_repository.delete_ids(to_remove)
    await _main_cities(repo=places_repository)


async def _save_enrich_data(  # noqa: WPS210, WPS231
    places: AsyncIterable[places_models_pb2.Place],
    repo: repository.PlacesRepository,
    osm_data: pd.DataFrame,
) -> None:
    updated = timestamp_pb2.Timestamp()
    updated.FromDatetime(datetime.datetime.now(tz=datetime.UTC))
    async for place in places:
        loc = place.location
        types = [models_pb2.Place.Type.ValueType(loc_types) for loc_types in loc.types]
        place_data = models_pb2.Place(
            id=loc.id,
            name=loc.name,
            no_accent_name=unidecode(loc.name),
            coordinates=latlng_pb2.LatLng(
                latitude=loc.coordinates.latitude,
                longitude=loc.coordinates.longitude,
            ),
            time_zone=loc.time_zone,
            country_code=loc.country_code,
            country_name=countries.get(alpha_2=loc.country_code).name,
            updated_at=updated,
            source_ref="junction",
            types=types,
            iata=place.place_attributes.iata,
        )

        if loc.types == [models_pb2.Place.TYPE_CITY]:
            # fmt: off
            osm_place = (
                osm_data[
                    (np.isclose(osm_data["lat"], loc.coordinates.latitude))
                    & (np.isclose(osm_data["long"], loc.coordinates.longitude))
                ].head(
                    1,
                ).replace(
                    {np.nan: None},
                ).to_dict(
                    orient="records",
                )[0]
            )
            # fmt: on

            population_str = "".join(
                char for char in osm_place.get("population") or "" if char.isdigit()
            )

            population = int(population_str) if population_str else 0

            place_data.population = population
            place_data.local_name = (
                osm_place["local_name"] if loc.country_code == "SE" else ""
            )
            place_data.no_accent_local_name = (
                unidecode(osm_place["local_name"]) if loc.country_code == "SE" else ""
            )

        await repo.insert(place_data)


async def _main_cities(
    repo: repository.PlacesRepository,
) -> None:
    async for place in await repo.find_non_cities():
        place_main_city = await repo.find_main_city(
            latitude=place.coordinates.latitude,
            longitude=place.coordinates.longitude,
            max_distance_meters=_CITY_RADIUS_M,
            types=models_pb2.Place.TYPE_CITY,
        )

        if place_main_city and place_main_city.name != place.main_city:
            place.main_city = place_main_city.name

        await repo.update(place)
