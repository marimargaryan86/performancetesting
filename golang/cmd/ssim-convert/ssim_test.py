import json
from pathlib import Path
from typing import TypedDict
from zoneinfo import available_timezones

from pydantic import confloat, constr, parse_obj_as

AIRLINES_PATH = Path(__file__).with_name("airlines.json")
AIRPORTS_PATH = Path(__file__).with_name("airports.json")
timezones = available_timezones()


class Airport(TypedDict):
    time_zone: str | None
    name: str
    longitude: confloat(  # type:ignore[valid-type]
        ge=-180,
        le=180,
    ) | None
    latitude: confloat(ge=-90, le=90) | None  # type:ignore[valid-type] # noqa: WPS432
    iata_code: constr(min_length=3, max_length=3)  # type:ignore[valid-type]


class TestSSIM(object):
    async def test_airlines(self) -> None:
        with AIRLINES_PATH.open() as fl:
            raw_data = json.load(fl)

        validated_airlines = parse_obj_as(
            list[constr(min_length=2, max_length=2)],  # type: ignore[index,misc]
            raw_data,
        )
        assert validated_airlines

    async def test_airports(self) -> None:
        with AIRPORTS_PATH.open() as fl:
            raw_data = json.load(fl)

        validated_airports = parse_obj_as(list[Airport], raw_data)
        assert validated_airports
        assert all(
            ap["time_zone"] in timezones
            for ap in validated_airports
            if ap["time_zone"] is not None
        )
