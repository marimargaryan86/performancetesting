import dataclasses
import zoneinfo
from typing import Any, Mapping, Optional, Sequence

from snowfall.junction.providers.ask2go import h3
from snowfall.vendor.ask2go.models import common


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
        coordinates: Mapping[str, Mapping[str, Any]],
        airports: Sequence[common.Airport],
    ):
        self._airports = {
            airport.iata: _make_airport(airport, coordinates[airport.iata])
            for airport in _filter_airports(airports, coordinates)
        }

    def get_by_iata(self, iata: str) -> Airport:
        return self._airports[iata]


def create_airports_mapping(
    coordinates: Mapping[str, Mapping[str, Any]],
    airports: Sequence[common.Airport],
) -> list[h3.CoordinatesItem[Airport]]:
    return [
        h3.CoordinatesItem[Airport](
            latitude=coordinates[airport.iata]["lat"],
            longitude=coordinates[airport.iata]["lon"],
            mapped_value=_make_airport(airport, coordinates[airport.iata]),
        )
        for airport in _filter_airports(airports, coordinates)
    ]


def _filter_airports(
    airports: Sequence[common.Airport],
    coordinates: Mapping[str, Mapping[str, Any]],
) -> list[common.Airport]:
    return [
        airport
        for airport in airports
        if airport.iata in coordinates
        and airport.language == "en"
        and airport.is_parent is False
    ]


def _make_airport(
    airport: common.Airport,
    airport_date: Mapping[str, Any],
) -> Airport:
    return Airport(
        airport_name=airport.airport_name,
        iata=airport.iata,
        timezone=zoneinfo.ZoneInfo(airport_date["tz"]),
        latitude=airport_date["lat"],
        longitude=airport_date["lon"],
    )
