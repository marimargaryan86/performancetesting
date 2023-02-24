import datetime
import random
from typing import Any, Mapping, Sequence, Union

import httpx
import numpy
import pandas
from google.protobuf import timestamp_pb2
from motor import motor_asyncio
from pycountry import countries
from unidecode import unidecode

from snowfall.project.junction.service.mobile_api import bootstrap, repository
from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1alpha import models_pb2 as stdlib_models_pb2

_SERVICE_NAME = "mobile-api"
_ATTRIBUTES_KEY = "attributes"


async def migrate(settings: bootstrap.Settings) -> None:  # noqa: WPS210
    mongo = motor_asyncio.AsyncIOMotorClient(settings.mongo_dsn)
    places_repository = repository.PlacesRepository(mongo[settings.mongo_db]["places"])
    http_client = httpx.AsyncClient(http2=True)
    auth_headers = {"Authorization": "Bearer {0}".format(settings.junction_api_token)}
    osm_data = pandas.read_csv(
        filesystem.resource_path(
            "snowfall.project.junction.service.mobile_api.main",
            "cities_populations.csv",
        ),
        sep=";",
        engine="python",
        encoding="utf8",
        on_bad_lines="skip",
    )
    places_response = await http_client.get(
        "{0}/places".format(random.choice(settings.junction_api_address)),  # nosec
        headers=auth_headers,
    )
    places_response.raise_for_status()
    json_response = places_response.json()
    await _save_enrich_data(json_response["data"], places_repository, osm_data)
    while len(json_response["data"]):
        places_response = await http_client.get(
            json_response["links"]["next"],
            headers=auth_headers,
        )
        places_response.raise_for_status()
        json_response = places_response.json()
        await _save_enrich_data(json_response["data"], places_repository, osm_data)


async def _save_enrich_data(
    places: Sequence[Mapping[str, Any]],
    repo: repository.PlacesRepository,
    osm_data: pandas.DataFrame,
) -> None:
    updated = timestamp_pb2.Timestamp()
    updated.FromDatetime(datetime.datetime.now(tz=datetime.timezone.utc))
    for place in places:
        attributes = place[_ATTRIBUTES_KEY]
        # fmt: off
        osm_place = (
            osm_data[
                (numpy.isclose(osm_data["lat"], attributes["latitude"]))
                & (numpy.isclose(osm_data["long"], attributes["longitude"]))
            ].head(
                1,
            ).replace(
                {numpy.nan: None},
            ).to_dict(
                orient="records",
            )[0]
        )
        # fmt: on

        population: Union[str, int] | None = "".join(
            char for char in osm_place.get("population", "") if char.isdigit()
        )
        population = int(population) if population else 0
        await repo.insert(
            models_pb2.Place(
                id=place["id"],
                name=attributes["name"],
                no_accent_name=unidecode(attributes["name"]),
                coordinates=stdlib_models_pb2.Coordinates(
                    latitude=attributes["latitude"],
                    longitude=attributes["longitude"],
                ),
                time_zone=attributes["timeZone"],
                country_code=attributes["countryCode"],
                country_name=countries.get(alpha_2=attributes["countryCode"]).name,
                updated_at=updated,
                source_ref="junction",
                types=[models_pb2.Place.Type.TYPE_UNSPECIFIED],
                population=population,
                local_name=(
                    osm_place["local_name"] if attributes["countryCode"] == "SE" else ""
                ),
                no_accent_local_name=(
                    unidecode(osm_place["local_name"])
                    if attributes["countryCode"] == "SE"
                    else ""
                ),
            ),
        )
