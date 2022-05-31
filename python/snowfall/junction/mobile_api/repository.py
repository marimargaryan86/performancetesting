import datetime

import pycountry
import rapidjson

from snowfall.junction.mobile_api import resources
from snowfall.stdlib.persistence import redis
from snowfall.vendor.junction import client

_PLACES_REDIS_KEY = "places"


class PlacesRepository(object):
    def __init__(
        self,
        junction_client: client.JunctionClient,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
    ) -> None:
        self._junction_client = junction_client
        self._redis = redis_client
        self._ttl = cache_ttl

    async def get(self) -> list[resources.PlaceResource]:
        places_response_json = await self._redis.get(_PLACES_REDIS_KEY)

        if places_response_json:
            return [
                resources.PlaceResource(**place)
                for place in rapidjson.loads(places_response_json)["data"]
            ]

        places_response = await self._junction_client.list_places()

        for place in places_response["data"]:
            place["attributes"]["countryName"] = pycountry.countries.get(
                alpha_2=place["attributes"]["countryCode"],
            ).name

        await self._put_to_cache(rapidjson.dumps(places_response))

        return [
            resources.PlaceResource(**place_enhanced)
            for place_enhanced in places_response["data"]
        ]

    async def _put_to_cache(self, places_json: str) -> None:
        await self._redis.put(_PLACES_REDIS_KEY, places_json)
        await self._redis.put_expires_at(
            _PLACES_REDIS_KEY,
            datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
        )
