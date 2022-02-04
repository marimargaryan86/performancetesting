from typing import Awaitable, Callable, Optional

import aioredis
import timezonefinder
from geopy import adapters, geocoders
from pycountry import countries

_LookupFunc = Callable[[float, float], Awaitable[Optional[str]]]


class ReverseGeocoder(object):
    def __init__(self, redis: aioredis.Redis, user_agent: str):
        self._redis = redis
        self._tz_finder = timezonefinder.TimezoneFinder()
        self._user_agent = user_agent
        self._country_lookup_funcs: list[_LookupFunc] = [
            self._photon_country_lookup,
            self._nominatim_country_lookup,
        ]

    async def get_country_code(self, latitude: float, longitude: float) -> str:
        return countries.get(
            alpha_2=(
                await self._cached_country_lookup(
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

    async def _cached_country_lookup(self, latitude: float, longitude: float) -> str:
        cache_key = "country_codes.{lat}_{lng}".format(
            lat=str(latitude).replace(".", "_"),
            lng=str(longitude).replace(".", "_"),
        )
        country_code = await self._redis.get(cache_key)

        if country_code:
            return country_code

        for lookup in self._country_lookup_funcs:
            country_code = await lookup(latitude, longitude)

            if country_code:
                await self._redis.set(cache_key, country_code)

                return country_code

        raise RuntimeError("Unable to find country for coordinates.")

    async def _photon_country_lookup(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[str]:
        async with geocoders.Photon(
            adapter_factory=adapters.AioHTTPAdapter,
            user_agent=self._user_agent,
        ) as geocoder:
            response = await geocoder.reverse(
                "{0}, {1}".format(latitude, longitude),
                exactly_one=True,
            )

        if not response:
            return None

        return response.raw["properties"]["countrycode"].upper()

    async def _nominatim_country_lookup(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[str]:
        async with geocoders.Nominatim(
            adapter_factory=adapters.AioHTTPAdapter,
            user_agent=self._user_agent,
        ) as geocoder:
            response = await geocoder.reverse(
                "{0}, {1}".format(latitude, longitude),
                exactly_one=True,
            )

        if not response:
            return None

        return response.raw["address"]["country_code"].upper()
