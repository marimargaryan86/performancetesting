import dataclasses
import zoneinfo
from typing import Mapping, Optional, Sequence

from snowfall.common.v1alpha import latlng_pb2
from snowfall.junction.providers.save_a_train import h3
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc


@dataclasses.dataclass(frozen=True)
class TrainStation(object):
    id: str  # noqa: A003
    name: Optional[str]
    timezone: zoneinfo.ZoneInfo
    latitude: float
    longitude: float


class TrainStationRepository(object):
    def __init__(
        self,
        train_stations: Sequence[TrainStation],
    ):
        self._train_stations = {station.id: station for station in train_stations}

    def get_by_id(self, train_station_id: str) -> TrainStation:
        return self._train_stations[train_station_id]


def create_train_stations_mapping(
    train_stations: Sequence[TrainStation],
) -> list[h3.CoordinatesItem[TrainStation]]:
    return [
        h3.CoordinatesItem[TrainStation](
            latitude=station.latitude,
            longitude=station.longitude,
            mapped_value=station,
        )
        for station in train_stations
    ]


async def make_train_station(
    train_station: Mapping[str, str],
    geocoder: geocoding_pb2_grpc.GeocodingServiceStub,
) -> TrainStation:
    latitude, longitude = map(float, train_station["coordinates"].split(","))
    return TrainStation(
        id=train_station["station_id"],
        name=train_station["station_name"],
        timezone=zoneinfo.ZoneInfo(
            (
                await geocoder.TimeZoneLookup(
                    geocoding_pb2.TimeZoneLookupRequest(
                        coordinates=latlng_pb2.LatLng(
                            latitude=latitude,
                            longitude=longitude,
                        ),
                    ),
                )
            ).time_zone.id,
        ),
        latitude=latitude,
        longitude=longitude,
    )
