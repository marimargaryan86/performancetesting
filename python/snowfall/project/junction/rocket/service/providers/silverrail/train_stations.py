import dataclasses
from collections.abc import Sequence

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


async def load_train_stations() -> list[TrainStation]:
    # TODO(regis.blanc): load the train from a JSON resource.
    return []
