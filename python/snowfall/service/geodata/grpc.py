from snowfall.common.v1alpha import datetime_pb2
from snowfall.service.geodata import geocoding
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib.persistence import redis
from snowfall.stdlib.transport import grpc


class GeocodingService(grpc.Service, geocoding_pb2_grpc.GeocodingServiceServicer):
    def __init__(self, cache: redis.Client[str], geocoder: geocoding.ReverseGeocoder):
        self._cache = cache
        self._geocoder = geocoder

    def get_name(self) -> str:
        return geocoding_pb2.DESCRIPTOR.services_by_name["GeocodingService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        geocoding_pb2_grpc.add_GeocodingServiceServicer_to_server(self, server)

    async def CountryCodeLookup(  # type: ignore[override] # noqa: N802
        self,
        request: geocoding_pb2.CountryCodeLookupRequest,
        context: grpc.aio.ServicerContext,
    ) -> geocoding_pb2.CountryCodeLookupResponse:
        cache_key = _make_cache_key(
            "country_codes",
            request.coordinates.latitude,
            request.coordinates.longitude,
        )

        country_code = await self._cache.get(cache_key)

        if not country_code:
            country_code = await self._geocoder.get_country_code(
                latitude=request.coordinates.latitude,
                longitude=request.coordinates.longitude,
            )

            await self._cache.put(cache_key, country_code)

        return geocoding_pb2.CountryCodeLookupResponse(
            country_code=country_code,
        )

    async def TimeZoneLookup(  # type: ignore[override] # noqa: N802
        self,
        request: geocoding_pb2.TimeZoneLookupRequest,
        context: grpc.aio.ServicerContext,
    ) -> geocoding_pb2.TimeZoneLookupResponse:
        cache_key = _make_cache_key(
            "timezones",
            request.coordinates.latitude,
            request.coordinates.longitude,
        )

        time_zone = await self._cache.get(cache_key)

        if not time_zone:
            time_zone = await self._geocoder.get_time_zone(
                latitude=request.coordinates.latitude,
                longitude=request.coordinates.longitude,
            )

            await self._cache.put(cache_key, time_zone)

        return geocoding_pb2.TimeZoneLookupResponse(
            time_zone=datetime_pb2.TimeZone(
                id=time_zone,
            ),
        )


def _make_cache_key(
    namespace: str,
    latitude: float,
    longitude: float,
) -> str:
    return "{namespace}.{lat}_{lng}".format(
        namespace=namespace,
        lat=str(latitude).replace(".", "_"),
        lng=str(longitude).replace(".", "_"),
    )
