import contextlib
import json
from collections.abc import Sequence

import aiofiles
import httpx

from snowfall.project.junction.service.providers.benerail import config
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.service import application, grpc_factory
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models.enumeration import position, response


async def dump_stations(
    app: application.Application[config.DumpStationsSettings],
) -> None:
    settings = app.settings

    async with httpx.AsyncClient(
        timeout=int(settings.api_timeout.total_seconds()),
        cert=config.cert_tmp_path(settings.cert_base64),
    ) as http_client:
        logging.register(http_client)
        metrics.register(http_client)
        benerail_client = client.BenerailClient(
            subscription_key=settings.subscription_key,
            base_url=str(settings.api_base_url),
            http_client=http_client,
        )
        cities_responses = await benerail_client.place.get_all_places(
            "META_STATION_HAFAS:Y",
        )

        geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
            await grpc_factory.make_insecure_channel(app, app.settings.geodata_address),
        )
        await _to_stations(
            cities_responses=cities_responses,
            geocoder=geocoder,
            output_file_path="/".join(
                [
                    str(settings.output_dir),
                    "benerail_stations.json",
                ],
            ),
        )


def get_cities_ids(
    cities_responses: Sequence[response.PlacesResponse | None],
) -> set[str]:
    city_ids: set[str] = set()

    for city_responses in cities_responses:
        if not city_responses or not city_responses.response_result:
            continue

        city_ids.update(
            place.identifier
            for place in (city_responses.response_result.places or [])
            if place.identifier is not None
        )

    return city_ids


async def _to_stations(  # noqa: WPS231
    cities_responses: Sequence[response.PlacesResponse],
    geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
    output_file_path: str,
) -> None:
    stations = []

    for response_obj in cities_responses:
        if not response_obj.response_result or not response_obj.response_result.places:
            continue

        for place_result in response_obj.response_result.places:
            name = ""

            if not isinstance(place_result.place, position.Station):
                continue

            if place_result.place.labels:
                with contextlib.suppress(KeyError):
                    name = place_result.place.labels["*"].code_long or ""

            stations.append(
                {
                    "id": (
                        place_result.place.codes.get("bnds")
                        if place_result.place.codes
                        else None
                    ),
                    "name": name,
                    "time_zone": (
                        await geocoder.TimeZoneLookup(
                            geocoding_pb2.TimeZoneLookupRequest(
                                coordinates=latlng_pb2.LatLng(
                                    latitude=float(
                                        (
                                            place_result.geo_coordinate.latitude
                                            if place_result.geo_coordinate
                                            else 0
                                        ),
                                    ),
                                    longitude=float(
                                        (
                                            place_result.geo_coordinate.longitude
                                            if place_result.geo_coordinate
                                            else 0
                                        ),
                                    ),
                                ),
                            ),
                        )
                    ).time_zone.id,
                    "latitude": float(
                        (
                            place_result.geo_coordinate.latitude
                            if place_result.geo_coordinate
                            else 0
                        ),
                    ),
                    "longitude": float(
                        (
                            place_result.geo_coordinate.longitude
                            if place_result.geo_coordinate
                            else 0
                        ),
                    ),
                },
            )

    async with aiofiles.open(output_file_path, "w") as out_file:
        await out_file.write(json.dumps(stations, indent=4))
