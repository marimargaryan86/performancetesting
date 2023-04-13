# type: ignore
import contextlib
import json
import random
from typing import Sequence

import aiofiles
import httpx

from snowfall.project.junction.service.providers.benerail import config
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.transport.grpc import client as grpc_client
from snowfall.stdlib.v1alpha import latlng_pb2
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models.enumeration import response


async def dump_stations(app: service.Application[config.DumpStationsSettings]) -> None:
    settings = app.settings

    async with httpx.AsyncClient(
        timeout=int(settings.api_timeout.total_seconds()),
        cert=(
            str(settings.cert_path),
            str(settings.private_key_path),
            settings.private_key_password,
        ),
    ) as http_client:
        logging.register(http_client)
        metrics.register(http_client)
        benerail_client = client.BenerailClient(
            subscription_key=settings.subscription_key,
            base_url=settings.api_base_url,
            http_client=http_client,
        )

        place_responses = await benerail_client.place.get_all_places()
        geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
            grpc_client.create_channel(
                random.choice(app.settings.geodata_address),  # nosec
            ),
        )
        await _to_stations(
            station_responses=place_responses,
            geocoder=geocoder,
            output_file_path="/".join(
                [
                    str(settings.output_dir),
                    "benerail_stations.json",
                ],
            ),
        )


async def _to_stations(
    station_responses: Sequence[response.PlacesResponse],
    geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
    output_file_path: str,
) -> None:
    stations = []

    for response_obj in station_responses:
        for place_result in response_obj.response_result.places:
            name = ""

            with contextlib.suppress(KeyError):
                name = place_result.place.labels["*"].code_long or ""

            stations.append(
                {
                    "id": place_result.place.codes.get("bnds"),
                    "name": name,
                    "time_zone": (
                        await geocoder.TimeZoneLookup(
                            geocoding_pb2.TimeZoneLookupRequest(
                                coordinates=latlng_pb2.LatLng(
                                    latitude=float(
                                        place_result.geo_coordinate.latitude,
                                    ),
                                    longitude=float(
                                        place_result.geo_coordinate.longitude,
                                    ),
                                ),
                            ),
                        )
                    ).time_zone.id,
                    "latitude": float(place_result.geo_coordinate.latitude),
                    "longitude": float(place_result.geo_coordinate.longitude),
                },
            )

    async with aiofiles.open(output_file_path, "w") as out_file:
        await out_file.write(json.dumps(stations, indent=4))
