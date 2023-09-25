import aiofiles
import orjson
from asyncstdlib import functools

from snowfall.stdlib import h3
from snowfall.stdlib.persistence import filesystem


@functools.cache
async def load_airports() -> h3.H3MappingRepository[h3.CoordinatesItem]:
    path = filesystem.resource_path("snowfall.data", "airports.json")

    async with aiofiles.open(path, "rb") as airports_file:
        airports = orjson.loads(await airports_file.read())

        return h3.H3MappingRepository[h3.CoordinatesItem](
            mapping=[
                h3.CoordinatesItem(
                    identifier=airport["iata_code"],
                    latitude=airport["latitude"],
                    longitude=airport["longitude"],
                    timezone=airport["time_zone"],
                )
                for airport in airports
                if airport["latitude"] and airport["longitude"]
            ],
            resolution=7,
        )


@functools.cache
async def load_benerail() -> h3.H3MappingRepository[h3.CoordinatesItem]:
    path = filesystem.resource_path(__name__, "benerail.json")

    async with aiofiles.open(path, "rb") as stations_file:
        stations = orjson.loads(await stations_file.read())

        return h3.H3MappingRepository[h3.CoordinatesItem](
            mapping=[
                h3.CoordinatesItem(
                    identifier=station["id"],
                    latitude=station["latitude"],
                    longitude=station["longitude"],
                    timezone=station["time_zone"],
                )
                for station in stations
                if station["latitude"] and station["longitude"]
            ],
            resolution=8,
        )


@functools.cache
async def load_direct_ferries() -> h3.H3MappingRepository[h3.CoordinatesItem]:
    path = filesystem.resource_path(__name__, "direct_ferries.json")

    async with aiofiles.open(path, "rb") as ports_file:
        ports = orjson.loads(await ports_file.read())

        return h3.H3MappingRepository[h3.CoordinatesItem](
            mapping=[
                h3.CoordinatesItem(
                    identifier=port["id"],
                    latitude=port["latitude"],
                    longitude=port["longitude"],
                    timezone=port["timezone"],
                )
                for port in ports
                if port["latitude"] and port["longitude"]
            ],
            resolution=8,
        )


@functools.cache
async def load_distribusion() -> h3.H3MappingRepository[h3.CoordinatesItem]:
    path = filesystem.resource_path(__name__, "distribusion.json")

    async with aiofiles.open(path, "rb") as stations_file:
        stations = orjson.loads(await stations_file.read())

        return h3.H3MappingRepository[h3.CoordinatesItem](
            mapping=[
                h3.CoordinatesItem(
                    identifier=station["id"],
                    latitude=station["latitude"],
                    longitude=station["longitude"],
                    timezone=station["time_zone"],
                )
                for station in stations
                if station["latitude"] and station["longitude"]
            ],
            resolution=8,
        )


@functools.cache
async def load_save_a_train() -> h3.H3MappingRepository[h3.CoordinatesItem]:
    path = filesystem.resource_path(__name__, "save_a_train.json")

    async with aiofiles.open(path, "rb") as stations_file:
        stations = orjson.loads(await stations_file.read())

        return h3.H3MappingRepository[h3.CoordinatesItem](
            mapping=[
                h3.CoordinatesItem(
                    identifier=station["id"],
                    latitude=station["latitude"],
                    longitude=station["longitude"],
                    timezone=station["time_zone"],
                )
                for station in stations
                if station["latitude"] and station["longitude"]
            ],
            resolution=8,
        )
