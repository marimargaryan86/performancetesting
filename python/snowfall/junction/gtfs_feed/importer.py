import dataclasses
import pathlib
from typing import Protocol

import aiofiles
import aioredis
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

    async def clear_cached_hash(self, feed_ref: str) -> None:
        await self._redis.delete(_CHECKSUM_KEY_FORMAT.format(ref=feed_ref))

    async def import_feed(
        self,
        zip_path: pathlib.Path,
        feed_ref: str,
        skip_checksum_check: bool,
    ) -> bool:
        current_checksum = await filesystem.hash_file(zip_path)
        cached_checksum = await self._redis.get(
            _CHECKSUM_KEY_FORMAT.format(ref=feed_ref),
        )

        if cached_checksum == current_checksum and not skip_checksum_check:
            self._logger.info("Feed has not changed since last import.")
            return False

        for zip_file in filesystem.unzip_file(zip_path):
            repo = self._repo_mapping.get(zip_file.name)

            if repo is not None:
                await repo.persist_csv_file(zip_file)
                self._logger.info(
                    "File imported successfully.",
                    filename=zip_file.name,
                )

        await self._redis.set(
            _CHECKSUM_KEY_FORMAT.format(ref=feed_ref),
            current_checksum,
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
