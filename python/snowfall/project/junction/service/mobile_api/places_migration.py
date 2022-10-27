import random
from typing import Any, Mapping, Sequence

import httpx
from geopy import adapters, geocoders
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
    async with geocoders.Nominatim(
        adapter_factory=adapters.AioHTTPAdapter,
    ) as geocoder:
        for place in places:
            response = await geocoder.reverse(
                "{0}, {1}".format(
                    place[_ATTRIBUTES_KEY]["latitude"],
                    place[_ATTRIBUTES_KEY]["longitude"],
                ),
                exactly_one=True,
            )

            if not response:
                raise RuntimeError

            country = countries.get(
                alpha_2=response.raw["address"]["country_code"].upper(),
            )
            place[_ATTRIBUTES_KEY]["countryCode"] = country.alpha_2
            place[_ATTRIBUTES_KEY]["countryName"] = country.name
    repo.insert_many(places)
