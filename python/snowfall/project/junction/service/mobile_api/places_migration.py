import random
from typing import Any, Mapping, Sequence

import httpx
from motor import motor_asyncio
from pycountry import countries

from snowfall.project.junction.service.mobile_api import bootstrap

_SERVICE_NAME = "mobile-api"
_ATTRIBUTES_KEY = "attributes"


async def migrate(settings: bootstrap.Settings) -> None:
    places_repository = motor_asyncio.AsyncIOMotorClient(settings.mongo_dsn)[  # nosec
        settings.mongo_db
    ]["places"]
    http_client = httpx.AsyncClient()
    auth_headers = {"Authorization": "Bearer {0}".format(settings.junction_api_token)}
    places_response = await http_client.get(
        "{0}/places".format(random.choice(settings.junction_api_address)),  # nosec
        headers=auth_headers,
    )
    json_response = places_response.json()
    await _save_enrich_data(json_response["data"], places_repository)
    while len(json_response["data"]):
        places_response = await http_client.get(
            json_response["links"]["next"],
            headers=auth_headers,
        )
        json_response = places_response.json()
        await _save_enrich_data(json_response["data"], places_repository)


async def _save_enrich_data(
    places: Sequence[Mapping[str, Any]],
    repo: motor_asyncio.AsyncIOMotorCollection,
) -> None:
    for place in places:
        country = countries.get(alpha_2=place[_ATTRIBUTES_KEY]["countryCode"])
        place[_ATTRIBUTES_KEY]["countryName"] = country.name

    repo.insert_many(places)
