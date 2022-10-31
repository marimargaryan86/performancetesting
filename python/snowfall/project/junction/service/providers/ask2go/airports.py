import dataclasses
import zoneinfo
from typing import Any, Iterator, Mapping, Optional, Sequence

from snowfall.stdlib import h3


@dataclasses.dataclass(frozen=True)
class Airport(object):
    airport_name: Optional[str]
    iata: str
    timezone: zoneinfo.ZoneInfo
    latitude: float
    longitude: float


class AirportRepository(object):
    def __init__(
        self,
        airports_data: Sequence[Mapping[str, Any]],
    ):
        self._airports = {
            airport["iata_code"]: _make_airport(airport)
            for airport in airports_data
            if airport["time_zone"] and airport["latitude"] and airport["longitude"]
        }

    def all_(self) -> Iterator[Airport]:
        yield from self._airports.values()

    def get_by_iata(self, iata: str) -> Airport:
        return self._airports[iata]


def create_airports_mapping(
    airports: AirportRepository,
) -> list[h3.CoordinatesItem[Airport]]:
    return [
        h3.CoordinatesItem[Airport](
            latitude=airport.latitude,
            longitude=airport.longitude,
            mapped_value=airport,
        )
        for airport in airports.all_()
    ]


def _make_airport(
    airport: Mapping[str, Any],
) -> Airport:
    return Airport(
        airport_name=airport["name"],
        iata=airport["iata_code"],
        timezone=zoneinfo.ZoneInfo(airport["time_zone"]),
        latitude=airport["latitude"],
        longitude=airport["longitude"],
    )
