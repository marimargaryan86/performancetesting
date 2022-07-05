import pathlib
from typing import Any, AsyncIterator, Type

import aiocsv
import aiofiles
import pymongo
from asyncstdlib import itertools

from snowfall.stdlib.format.gtfs import models
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset

_SERVICE_ID = "service_id"
_TUPLE_OF_CSV = tuple[dict[str, str], ...]


def _no_empty_values(dict_tuple: tuple[str, str]) -> bool:
    return dict_tuple[1] != ""


class Repository(repository.PydanticRepository[repository.Model]):
    _defaults: dict[str, Any] = {}
    _model: Type[repository.Model]

    async def persist_csv_file(self, path: pathlib.Path) -> None:
        async with aiofiles.open(str(path)) as csv_file:
            args = [aiocsv.AsyncDictReader(csv_file)] * 100  # noqa: WPS435
            chunks: AsyncIterator[_TUPLE_OF_CSV] = itertools.zip_longest(
                *args,
                fillvalue=None,
            )

            async for rows in chunks:
                normalized_rows = self._normalize_rows(rows)

                await self._execute(
                    self._collection.insert_many,
                    [self._coder.encode(row) for row in normalized_rows],
                    ordered=False,
                )

    def _normalize_rows(
        self,
        rows: _TUPLE_OF_CSV,
    ) -> list[repository.Model]:
        new_rows = []

        for row in rows:
            if not row:
                break

            row = {item_k: item_v.strip() for item_k, item_v in row.items()}
            row = dict(filter(_no_empty_values, row.items()))

            for item_k, item_v in (self._defaults or {}).items():
                row[item_k] = row.get(item_k, item_v)

            new_rows.append(self._model.parse_obj(row))

        return new_rows


class AgencyRepository(mixins.AllMixin[models.Agency], Repository[models.Agency]):
    _indexes = [pymongo.IndexModel("agency_id", background=True, unique=True)]
    _defaults: dict[str, Any] = {}
    _model = models.Agency

    async def get_by_id(
        self,
        agency_id: str,
    ) -> models.Agency:
        agency = await self._execute(
            self._collection.find_one,
            {
                "agency_id": agency_id,
            },
        )

        if not agency:
            raise RuntimeError(
                "Unable to find agency {agency}.".format(agency=agency_id),
            )

        return agency


class CalendarRepository(Repository[models.Calendar]):
    _indexes = [pymongo.IndexModel(_SERVICE_ID, background=True)]
    _model = models.Calendar

    async def find_by_service_id(
        self,
        service_id: str,
    ) -> resultset.ResultSet[models.Calendar]:
        return await self._execute(
            self._collection.find,
            {
                _SERVICE_ID: service_id,
            },
        )


class CalendarDateRepository(Repository[models.CalendarDate]):
    _indexes = [pymongo.IndexModel(_SERVICE_ID, background=True)]
    _model = models.CalendarDate

    async def find_by_service_id(
        self,
        service_id: str,
    ) -> resultset.ResultSet[models.CalendarDate]:
        return await self._execute(
            self._collection.find,
            {
                _SERVICE_ID: service_id,
            },
        )


class RouteRepository(Repository[models.Route]):
    _indexes = [pymongo.IndexModel("route_id", background=True, unique=True)]
    _model = models.Route

    async def get_by_id(
        self,
        route_id: str,
    ) -> models.Route:
        route = await self._execute(
            self._collection.find_one,
            {
                "route_id": route_id,
            },
        )

        if not route:
            raise RuntimeError("Unable to find route {route}.".format(route=route_id))

        return route


class StopRepository(mixins.AllMixin[models.Stop], Repository[models.Stop]):
    _indexes = [pymongo.IndexModel("stop_id", background=True, unique=True)]
    _defaults = {
        "location_type": 0,
        "wheelchair_boarding": 0,
    }
    _model = models.Stop

    async def find_by_ids(
        self,
        *stop_id: str,
    ) -> resultset.ResultSet[models.Stop]:
        return await self._execute(
            self._collection.find,
            {
                "stop_id": {
                    "$in": stop_id,
                },
            },
        )


class StopTimeRepository(Repository[models.StopTime]):
    _indexes = [pymongo.IndexModel("trip_id", background=True)]
    _defaults = {
        "pickup_type": 0,
        "drop_off_type": 0,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "timepoint": 1,
    }
    _model = models.StopTime

    async def find_by_trip_id(
        self,
        trip_id: str,
    ) -> resultset.ResultSet[models.StopTime]:
        return await self._execute(
            self._collection.find,
            {
                "trip_id": trip_id,
            },
        )


class TripRepository(mixins.AllMixin[models.Trip], Repository[models.Trip]):
    _indexes = [
        pymongo.IndexModel("route_id", background=True),
        pymongo.IndexModel(_SERVICE_ID, background=True),
        pymongo.IndexModel("trip_id", background=True, unique=True),
    ]
    _defaults = {
        "bikes_allowed": 0,
        "wheelchair_accessible": 0,
    }
    _model = models.Trip
