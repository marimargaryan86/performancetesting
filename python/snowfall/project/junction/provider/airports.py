import dataclasses
import zoneinfo
from collections.abc import Iterator, Mapping, Sequence
from typing import Any

from snowfall.stdlib import h3


@dataclasses.dataclass(frozen=True)
class Airport(h3.CoordinatesItem):
    airport_name: str | None
    iata_country_code: str


class AirportRepository:
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


def _make_airport(
    airport: Mapping[str, Any],
) -> Airport:
    return Airport(
        identifier=airport["iata_code"],
        airport_name=airport["name"],
        timezone=zoneinfo.ZoneInfo(airport["time_zone"]),
        latitude=airport["latitude"],
        longitude=airport["longitude"],
        iata_country_code=airport["iata_country_code"],
    )
