import dataclasses
import pathlib
from typing import AsyncGenerator, Protocol

import aiofiles
import aioredis
import asyncstdlib
import httpx
import structlog
from motor import core

from snowfall.junction.gtfs_feed import repository
from snowfall.stdlib.persistence import filesystem

_CHECKSUM_KEY_FORMAT = "feeds.{ref}.checksum"


class _CsvImporter(Protocol):
    async def persist_csv_file(self, path: pathlib.Path) -> None:
        """Interface for repository.Repository to make Mypy happy."""


@dataclasses.dataclass(frozen=True)
class RepositoryCollection(object):
    agencies: repository.AgencyRepository
    calendars: repository.CalendarRepository
    calendar_dates: repository.CalendarDateRepository
    routes: repository.RouteRepository
    stops: repository.StopRepository
    stop_times: repository.StopTimeRepository
    trips: repository.TripRepository

    @classmethod
    def create_for_database(
        cls,
        database: core.AgnosticDatabase,
    ) -> "RepositoryCollection":
        return cls(
            agencies=repository.AgencyRepository(database.agencies),
            calendars=repository.CalendarRepository(database.calendars),
            calendar_dates=repository.CalendarDateRepository(database.calendar_dates),
            routes=repository.RouteRepository(database.routes),
            stops=repository.StopRepository(database.stops),
            stop_times=repository.StopTimeRepository(database.stop_times),
            trips=repository.TripRepository(database.trips),
        )


class Importer(object):
    def __init__(
        self,
        redis: aioredis.Redis,
        repositories: RepositoryCollection,
        path: pathlib.Path,
    ):
        self._logger = structlog.get_logger(__name__)
        self._path = path
        self._redis = redis
        self._repo_mapping: dict[str, _CsvImporter] = {
            "agency.txt": repositories.agencies,
            "calendar.txt": repositories.calendars,
            "calendar_dates.txt": repositories.calendar_dates,
            "routes.txt": repositories.routes,
            "stops.txt": repositories.stops,
            "stop_times.txt": repositories.stop_times,
            "trips.txt": repositories.trips,
        }

    @asyncstdlib.contextmanager
    async def cache_hash(
        self,
        zip_path: pathlib.Path,
        feed_ref: str,
    ) -> AsyncGenerator[bool, None]:
        current_checksum = await filesystem.hash_file(zip_path)
        cached_checksum = await self._redis.get(
            _CHECKSUM_KEY_FORMAT.format(ref=feed_ref),
        )

        yield cached_checksum == current_checksum

        await self._redis.set(
            _CHECKSUM_KEY_FORMAT.format(ref=feed_ref),
            current_checksum,
        )

    async def import_feed(
        self,
        zip_path: pathlib.Path,
    ) -> bool:
        for zip_file in filesystem.unzip_file(zip_path):
            repo = self._repo_mapping.get(zip_file.name)

            if repo is not None:
                await repo.persist_csv_file(zip_file)
                self._logger.info(
                    "File imported successfully.",
                    filename=zip_file.name,
                )

        return True

    async def _write_file(
        self,
        response: httpx.Response,
        filename: pathlib.Path,
    ) -> None:
        async with aiofiles.open(str(filename), mode="wb") as feed_file:
            async for chunk in response.aiter_bytes():
                await feed_file.write(chunk)
