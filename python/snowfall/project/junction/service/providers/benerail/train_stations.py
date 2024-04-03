import dataclasses
import json
import pkgutil
import zoneinfo
from collections.abc import Mapping, Sequence

from snowfall.stdlib import h3


@dataclasses.dataclass(frozen=True)
class TrainStation(h3.CoordinatesItem):
    name: str | None


class TrainStationRepository:
    def __init__(
        self,
        train_stations: Sequence[TrainStation],
    ):
        self._train_stations = {
            station.identifier: station for station in train_stations
        }

    def get_by_id(self, train_station_id: str) -> TrainStation:
        try:
            return self._train_stations[train_station_id]
        except KeyError:
            return self._train_stations["urn:bnds:tstatn_id:FRPNO"]

    def resolve_place_with_urn(
        self,
        urn: str,
    ) -> TrainStation:
        place_id = "urn:bnds:tstatn_id:{0}".format(urn.rsplit(":", 1)[-1])
        return self.get_by_id(place_id)


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


async def load_train_stations() -> list[TrainStation]:
    json_content = pkgutil.get_data(
        "snowfall.project.junction.service.providers.benerail.main",
        "benerail_stations.json",
    )

    if json_content is None:
        raise RuntimeError("benerail_stations.json not found")

    stations = json.loads(json_content.decode("utf-8"))
    return [await make_train_station(station) for station in stations]
