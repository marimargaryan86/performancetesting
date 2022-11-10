import datetime
import random
from typing import Any, Mapping, Sequence

import httpx
from google.protobuf import timestamp_pb2
from motor import motor_asyncio
from pycountry import countries

from snowfall.project.junction.service.mobile_api import bootstrap, repository
from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.v1alpha import models_pb2 as stdlib_models_pb2

_SERVICE_NAME = "mobile-api"
_ATTRIBUTES_KEY = "attributes"


async def migrate(settings: bootstrap.Settings) -> None:  # noqa: WPS210
    mongo = motor_asyncio.AsyncIOMotorClient(settings.mongo_dsn)
    places_repository = repository.PlacesRepository(mongo[settings.mongo_db]["places"])
    http_client = httpx.AsyncClient(http2=True)
    auth_headers = {"Authorization": "Bearer {0}".format(settings.junction_api_token)}
    places_response = await http_client.get(
        "{0}/places".format(random.choice(settings.junction_api_address)),  # nosec
        headers=auth_headers,
    )
    places_response.raise_for_status()
    json_response = places_response.json()
    await _save_enrich_data(json_response["data"], places_repository)
    while len(json_response["data"]):
        places_response = await http_client.get(
            json_response["links"]["next"],
            headers=auth_headers,
        )
        places_response.raise_for_status()
        json_response = places_response.json()
        await _save_enrich_data(json_response["data"], places_repository)


async def _save_enrich_data(
    places: Sequence[Mapping[str, Any]],
    repo: repository.PlacesRepository,
) -> None:
    updated = timestamp_pb2.Timestamp()
    updated.FromDatetime(datetime.datetime.now(tz=datetime.timezone.utc))
    for place in places:
        attributes = place[_ATTRIBUTES_KEY]
        country = countries.get(alpha_2=attributes["countryCode"])
        await repo.insert(
            models_pb2.Place(
                id=place["id"],
                name=attributes["name"],
                coordinates=stdlib_models_pb2.Coordinates(
                    latitude=attributes["latitude"],
                    longitude=attributes["longitude"],
                ),
                time_zone=attributes["timeZone"],
                country_code=attributes["countryCode"],
                country_name=country.name,
                updated_at=updated,
                source_ref="junction",
                types=[models_pb2.Place.Type.TYPE_UNSPECIFIED],
            ),
        )
