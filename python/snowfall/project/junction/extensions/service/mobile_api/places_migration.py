import datetime
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
from snowfall.project.junction.go.service.places.v1alpha.models_pb2 import Place
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import latlng_pb2

_SERVICE_NAME = "mobile-api"
_ATTRIBUTES_KEY = "attributes"


async def migrate(settings: bootstrap.MigrateSettings) -> None:  # noqa: WPS210
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


async def _save_enrich_data(  # noqa: WPS210
    places: AsyncIterable[Place],
    repo: repository.PlacesRepository,
    osm_data: pd.DataFrame,
) -> None:
    updated = timestamp_pb2.Timestamp()
    updated.FromDatetime(datetime.datetime.now(tz=datetime.UTC))
    async for place in places:
        loc = place.location
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
        await repo.insert(
            models_pb2.Place(
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
                types=[models_pb2.Place.Type.TYPE_UNSPECIFIED],
                population=population,
                local_name=(
                    osm_place["local_name"] if loc.country_code == "SE" else ""
                ),
                no_accent_local_name=(
                    unidecode(osm_place["local_name"])
                    if loc.country_code == "SE"
                    else ""
                ),
            ),
        )
