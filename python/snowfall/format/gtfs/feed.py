import dataclasses
import datetime
import pathlib
import uuid
import weakref
import zipfile
import zoneinfo
from typing import Any, AsyncIterator, Optional, Type, Union

import aiocsv
import aiofiles
import pydantic

from snowfall.format.gtfs import constants, datetimes, models

_FEED_INFO = "feed_info"
_ParsedFilesDict = dict[
    str,
    Union[Optional[pydantic.BaseModel], list[pydantic.BaseModel]],
]


def _unzip(path: pathlib.Path) -> set[str]:
    with zipfile.ZipFile(str(path)) as zip_handle:
        if zip_handle.testzip():
            raise RuntimeError(
                "{filename} is not a valid zip file".format(filename=str(path)),
            )

        zip_handle.extractall(str(path.parent))

        return {file_in_zip.filename for file_in_zip in zip_handle.filelist}


@dataclasses.dataclass(frozen=True)
class _FileInfo(object):
    arg: str
    filename: str
    model: Type[pydantic.BaseModel]
    defaults: Optional[dict[str, Any]] = None
    optional: bool = False


class Parser(object):
    _files: list[_FileInfo] = [
        _FileInfo(arg="agencies", filename="agency.txt", model=models.Agency),
        _FileInfo(
            arg="calendars",
            filename="calendar.txt",
            model=models.Calendar,
            optional=True,
        ),
        _FileInfo(
            arg="calendar_dates",
            filename="calendar_dates.txt",
            model=models.CalendarDate,
            optional=True,
        ),
        _FileInfo(
            arg=_FEED_INFO,
            filename="feed_info.txt",
            model=models.FeedInfo,
            optional=True,
        ),
        _FileInfo(arg="routes", filename="routes.txt", model=models.Route),
        _FileInfo(
            arg="stop_times",
            filename="stop_times.txt",
            model=models.StopTime,
            defaults={
                "pickup_type": 0,
                "drop_off_type": 0,
                "continuous_pickup": 1,
                "continuous_drop_off": 1,
                "timepoint": 1,
            },
        ),
        _FileInfo(
            arg="stops",
            filename="stops.txt",
            model=models.Stop,
            defaults={
                "location_type": 0,
                "wheelchair_boarding": 0,
            },
        ),
        _FileInfo(
            arg="trips",
            filename="trips.txt",
            model=models.Trip,
            defaults={
                "bikes_allowed": 0,
                "wheelchair_accessible": 0,
            },
        ),
    ]

    def __init__(self, ref: str):
        self._ref = ref

    async def parse_zip(
        self,
        zip_path: pathlib.Path,
    ) -> models.Feed:
        names = _unzip(zip_path)
        parsed_files: _ParsedFilesDict = {}

        for csv_file in self._files:
            if csv_file.filename not in names:
                if csv_file.optional:
                    parsed_files[csv_file.arg] = []
                    continue

                raise RuntimeError(
                    "{0} not found in zip file".format(csv_file.filename),
                )

            parsed_files[csv_file.arg] = [
                model async for model in _parse_file(zip_path.parent, csv_file)
            ]

        # feed_info.txt is always one row
        if parsed_files[_FEED_INFO]:
            parsed_files[_FEED_INFO] = parsed_files[_FEED_INFO][0]  # type: ignore[index]
        else:
            parsed_files[_FEED_INFO] = None

        return models.Feed(ref=self._ref, **parsed_files)  # type: ignore[arg-type]


async def _parse_file(
    filedir: pathlib.Path,
    fileinfo: _FileInfo,
) -> AsyncIterator[pydantic.BaseModel]:
    async with aiofiles.open(str(filedir.joinpath(fileinfo.filename))) as csv_file:
        async for row in aiocsv.AsyncDictReader(csv_file):
            row = {item_k: item_v.strip() for item_k, item_v in row.items()}
            row = dict(filter(_no_empty_values, row.items()))

            for item_k, item_v in (fileinfo.defaults or {}).items():
                row[item_k] = row.get(item_k, item_v)

            yield fileinfo.model.parse_obj(row)


def _no_empty_values(dict_tuple: tuple[str, str]) -> bool:
    return dict_tuple[1] != ""


class FeedDecorator(object):
    def __init__(self, feed: models.Feed):
        self.feed: models.Feed = feed
        self.namespace: uuid.UUID = uuid.uuid5(constants.NAMESPACE, feed.ref)
        self.time_zone: datetime.tzinfo = zoneinfo.ZoneInfo(
            feed.agencies[0].agency_timezone,
        )
        self._agency_map: dict[str, weakref.ref[models.Agency]] = {
            agency.agency_id or "": weakref.ref(agency) for agency in feed.agencies
        }
        self._route_map: dict[str, weakref.ref[models.Route]] = {
            route.route_id: weakref.ref(route) for route in feed.routes
        }
        self._service_dates_map = datetimes.create_service_dates_map(feed)
        self._stop_map: dict[str, weakref.ref[models.Stop]] = {
            stop.stop_id: weakref.ref(stop) for stop in feed.stops
        }
        self._trip_map: dict[str, weakref.ref[models.Trip]] = {
            trip.trip_id: weakref.ref(trip) for trip in feed.trips
        }

    def get_agency_by_id(self, identifier: str) -> models.Agency:
        agency = self._agency_map[identifier]()

        if not agency:
            raise KeyError()

        return agency

    def get_service_dates_by_service_id(self, identifier: str) -> list[datetime.date]:
        return self._service_dates_map[identifier]

    def get_stop_by_id(self, identifier: str) -> models.Stop:
        stop = self._stop_map[identifier]()

        if not stop:
            raise KeyError()

        return stop

    def get_route_by_id(self, identifier: str) -> models.Route:
        route = self._route_map[identifier]()

        if not route:
            raise KeyError()

        return route

    def get_trip_by_id(self, identifier: str) -> models.Trip:
        trip = self._trip_map[identifier]()

        if not trip:
            raise KeyError()

        return trip
