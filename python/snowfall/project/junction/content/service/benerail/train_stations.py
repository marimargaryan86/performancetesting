import dataclasses
import json
import pkgutil
import zoneinfo
from collections.abc import Sequence

from snowfall.stdlib import h3


@dataclasses.dataclass(frozen=True)
class TrainStation(h3.CoordinatesItem):
    name: str | None


class TrainStationRepository(object):
    def __init__(
        self,
        stations: Sequence[TrainStation],
    ):
        self._train_stations = {station.identifier: station for station in stations}

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


def load_train_stations() -> list[TrainStation]:
    json_content = pkgutil.get_data(
        "snowfall.project.junction.content.service.benerail.train_stations",
        "benerail_stations.json",
    )

    if json_content is None:
        raise RuntimeError("benerail_stations.json not found")

    stations = json.loads(json_content.decode("utf-8"))
    return [
        TrainStation(
            identifier=str(station["id"]),
            name=str(station["name"]),
            timezone=zoneinfo.ZoneInfo(str(station["time_zone"])),
            latitude=float(station["latitude"]),
            longitude=float(station["longitude"]),
        )
        for station in stations
    ]
