import dataclasses
import json
import pathlib
import zoneinfo
from typing import Mapping, Optional, Sequence

import aiofiles

from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib import h3
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.save_a_train.models.misc import VendorStationsResponse


@dataclasses.dataclass(frozen=True)
class TrainStation(h3.CoordinatesItem):
    name: Optional[str]


class TrainStationRepository(object):
    def __init__(
        self,
        train_stations: Sequence[TrainStation],
    ):
        self._train_stations = {
            station.identifier: station for station in train_stations
        }

    def get_by_id(self, train_station_id: str) -> TrainStation:
        return self._train_stations[train_station_id]


async def dump_sat_stations(
    geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
    response: VendorStationsResponse,
    output_file: pathlib.Path,
) -> None:
    stations = []

    for station in response.stations:
        if not station.searchable or not station.location:
            continue

        latitude, longitude = str(station.location).split(",")

        stations.append(
            {
                "id": station.uid,
                "name": station.name,
                "time_zone": (
                    await geocoder.TimeZoneLookup(
                        geocoding_pb2.TimeZoneLookupRequest(
                            coordinates=latlng_pb2.LatLng(
                                latitude=float(latitude),
                                longitude=float(longitude),
                            ),
                        ),
                    )
                ).time_zone.id,
                "latitude": float(latitude),
                "longitude": float(longitude),
            },
        )

    async with aiofiles.open(str(output_file), "w") as out_file:
        await out_file.write(json.dumps(stations, indent=4))


async def make_train_station(
    train_station: Mapping[str, str | float],
) -> TrainStation:
    return TrainStation(
        identifier=str(train_station["id"]),
        name=str(train_station["name"]),
        timezone=zoneinfo.ZoneInfo(str(train_station["time_zone"])),
        latitude=float(train_station["latitude"]),
        longitude=float(train_station["longitude"]),
    )
