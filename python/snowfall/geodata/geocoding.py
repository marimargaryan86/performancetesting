import aioredis
import timezonefinder
from geopy import adapters, geocoders
from pycountry import countries


class ReverseGeocoder(object):
    def __init__(self, redis: aioredis.Redis, user_agent: str):
        self._redis = redis
        self._tz_finder = timezonefinder.TimezoneFinder()
        self._user_agent = user_agent

    async def get_country_code(self, latitude: float, longitude: float) -> str:
        return countries.get(
            alpha_2=(
                await self._photon_lookup(
                    latitude=latitude,
                    longitude=longitude,
                )
            ),
        ).alpha_2

    async def get_time_zone(self, latitude: float, longitude: float) -> str:
        return self._tz_finder.timezone_at(
            lat=latitude,
            lng=longitude,
        )

    async def _photon_lookup(self, latitude: float, longitude: float) -> str:
        cache_key = "country_codes.{lat}_{lng}".format(
            lat=str(latitude).replace(".", "_"),
            lng=str(longitude).replace(".", "_"),
        )
        country_code = await self._redis.get(cache_key)

        if not country_code:
            async with geocoders.Photon(
                adapter_factory=adapters.AioHTTPAdapter,
                user_agent=self._user_agent,
            ) as geocoder:
                country_code = (
                    await geocoder.reverse(
                        "{0}, {1}".format(latitude, longitude),
                        exactly_one=True,
                    )
                ).raw["properties"]["countrycode"]

            await self._redis.set(cache_key, country_code)

        return country_code
