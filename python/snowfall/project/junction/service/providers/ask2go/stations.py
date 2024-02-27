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
    station_response = await ask2go_client.get_train_stations()
    stations = [
        {
            "identifier": ts["code"],
            "name": ts["name"],
            "timezone": (
                await geocoder.TimeZoneLookup(
                    geocoding_pb2.TimeZoneLookupRequest(
                        coordinates=latlng_pb2.LatLng(
                            latitude=ts["latitude"],
                            longitude=ts["longtitude"],
                        ),
                    ),
                )
            ).time_zone.id,
            "latitude": ts["latitude"],
            "longitude": ts["longtitude"],
            "is_enabled": ts["isEnabled"],
            "iata_country_code": ts["country"],
            "railname": ts["railname"],
        }
        for ts in station_response.json()
        if ts["isEnabled"]
    ]

    async with aiofiles.open(output_file_path, "w") as out_file:
        await out_file.write(json.dumps(stations, indent=4))
