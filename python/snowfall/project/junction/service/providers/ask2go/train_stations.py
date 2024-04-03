import dataclasses
from collections.abc import Collection, Iterator

from snowfall.project.junction.provider.airports import Airport

ASK2GO_STATIONS_PACKAGE = "snowfall.project.junction.service.providers.ask2go.main"
ASK2GO_RESOURCE = "ask2go_stations.json"


@dataclasses.dataclass(frozen=True)
class TrainStation(Airport):
    is_enabled: bool
    railname: str


class TrainStationRepository:
    def __init__(self, train_stations: Collection[TrainStation]):
        self._by_code = {ts.identifier: ts for ts in train_stations}

    def all_(self) -> Iterator[TrainStation]:
        yield from self._by_code.values()

    def retrieve_by_code(self, code: str) -> TrainStation:
        return self._by_code[code]
