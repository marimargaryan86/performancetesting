import json

import aiofiles

from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.ask2go import client


async def dump_stations(
    geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
    ask2go_client: client.Ask2GoClient,
    output_file_path: str,
) -> None:
    station_responses = await ask2go_client.get_train_stations()
    stations = [
        {
            "id": station.identifier,
            "name": station.name,
            "time_zone": (
                await geocoder.TimeZoneLookup(
                    geocoding_pb2.TimeZoneLookupRequest(
                        coordinates=latlng_pb2.LatLng(
                            latitude=station.latitude,
                            longitude=station.longtitude,
                        ),
                    ),
                )
            ).time_zone.id,
            "latitude": station.latitude,
            "longitude": station.longtitude,
        }
        for station in station_responses
    ]

    async with aiofiles.open(output_file_path, "w") as out_file:
        await out_file.write(json.dumps(stations, indent=4))
