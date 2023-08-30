import asyncio
from collections.abc import Awaitable, Callable

import shapefile
import tenacity
import timezonefinder
from geopy import adapters, geocoders
from pycountry import countries
from shapely import geometry

_LookupFunc = Callable[[float, float], Awaitable[str | None]]  # noqa: WPS465


class Geocoder(object):
    def __init__(
        self,
        shp_file: shapefile.Reader,
        user_agent: str,
    ):
        self._records = shp_file.shapeRecords()
        self._shapes = [
            {
                "shape": geometry.shape(shape_record.shape),
                "alpha_3": shape_record.record["ISO_SOV1"],
            }
            for shape_record in self._records
        ]
        self._tz_finder = timezonefinder.TimezoneFinder()
        self._user_agent = user_agent
        self._country_lookup_funcs: list[_LookupFunc] = [
            self._offline_country_lookup,
            self._photon_country_lookup,
            self._nominatim_country_lookup,
        ]

    async def get_country_code(self, latitude: float, longitude: float) -> str:
        country = countries.get(
            alpha_2=(
                await self._country_lookup(
                    latitude=latitude,
                    longitude=longitude,
                )
            ),
        )

        if not country:
            raise ValueError("Unknown country code")

        return country.alpha_2

    async def get_time_zone(self, latitude: float, longitude: float) -> str:
        time_zone = self._tz_finder.timezone_at(
            lat=latitude,
            lng=longitude,
        )

        if not time_zone:
            raise RuntimeError("Unable to determine time zone")

        return time_zone

    async def _country_lookup(self, latitude: float, longitude: float) -> str:
        for lookup in self._country_lookup_funcs:
            country_code = await lookup(latitude, longitude)

            if country_code:
                return country_code

        raise RuntimeError("Unable to find country for coordinates.")

    async def _offline_country_lookup(  # noqa: WPS231
        self,
        latitude: float,
        longitude: float,
    ) -> str | None:
        # Iterate over copy of list, as we modify on found country.
        for ind, shape_record in enumerate(self._shapes[:]):
            if geometry.Point(longitude, latitude).within(shape_record["shape"]):
                country = countries.get(
                    alpha_3=shape_record["alpha_3"],
                )

                if not country:
                    raise ValueError("Unknown country code")

                # When a sequence of requests come in, the same result is usually found
                # for several requests in a row. Therefore, move the found record to
                # the front so it is checked first in subsequent requests.
                if ind > 0:
                    self._records.insert(0, self._records.pop(ind))

                return country.alpha_2

            # Ensure we yield back to event loop frequently.
            if ind % 10 == 9:
                await asyncio.sleep(0)

        return None

    @tenacity.retry(
        stop=tenacity.stop_after_delay(20),  # noqa: WPS432
        wait=tenacity.wait_random_exponential(multiplier=1, max=5),
        reraise=True,
    )
    async def _photon_country_lookup(
        self,
        latitude: float,
        longitude: float,
    ) -> str | None:
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

    @tenacity.retry(
        stop=tenacity.stop_after_delay(20),  # noqa: WPS432
        wait=tenacity.wait_random_exponential(multiplier=1, max=5),
        reraise=True,
    )
    async def _nominatim_country_lookup(
        self,
        latitude: float,
        longitude: float,
    ) -> str | None:
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
