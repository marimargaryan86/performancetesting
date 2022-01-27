import pathlib
import zipfile
from typing import Any, AsyncIterable, Mapping, Optional, Type, TypeVar

import aiocsv
import aiofiles
import pydantic

from snowfall.format.gtfs import models

Model = TypeVar("Model", bound=pydantic.BaseModel)


def _no_empty_values(dict_tuple: tuple[str, str]) -> bool:
    return dict_tuple[1] != ""


async def _parse_file(
    path: pathlib.Path,
    model: Type[Model],
    defaults: Optional[Mapping[str, Any]] = None,
) -> AsyncIterable[Model]:
    async with aiofiles.open(str(path)) as csv_file:
        async for row in aiocsv.AsyncDictReader(csv_file):
            row = {item_k: item_v.strip() for item_k, item_v in row.items()}
            row = dict(filter(_no_empty_values, row.items()))

            for item_k, item_v in (defaults or {}).items():
                row[item_k] = row.get(item_k, item_v)

            yield model.parse_obj(row)


def _unzip(path: pathlib.Path) -> set[str]:
    with zipfile.ZipFile(str(path)) as zip_handle:
        if zip_handle.testzip():
            raise RuntimeError(
                "{filename} is not a valid zip file".format(filename=str(path)),
            )

        zip_handle.extractall(str(path.parent))

        return {file_in_zip.filename for file_in_zip in zip_handle.filelist}


async def load_from_zip(path: pathlib.Path) -> models.Feed:
    names = _unzip(path)
    feed_info = None
    calendars = None
    calendar_dates = None

    if "calendar.txt" in names:
        calendars = _parse_file(
            path.parent.joinpath("calendar.txt"),
            models.Calendar,
        )

    if "calendar_dates.txt" in names:
        calendar_dates = _parse_file(
            path.parent.joinpath("calendar_dates.txt"),
            models.CalendarDate,
        )

    if "feed_info.txt" in names:
        feed_info = [
            feed_info
            async for feed_info in _parse_file(
                path.parent.joinpath("feed_info.txt"),
                models.FeedInfo,
            )
        ][0]

    return models.Feed(
        agencies=_parse_file(path.parent.joinpath("agency.txt"), models.Agency),
        calendars=calendars,
        calendar_dates=calendar_dates,
        feed_info=feed_info,
        routes=_parse_file(path.parent.joinpath("routes.txt"), models.Route),
        stops=_parse_file(
            path.parent.joinpath("stops.txt"),
            models.Stop,
            {
                "location_type": 0,
                "wheelchair_boarding": 0,
            },
        ),
        trips=_parse_file(
            path.parent.joinpath("trips.txt"),
            models.Trip,
            {
                "bikes_allowed": 0,
                "wheelchair_accessible": 0,
            },
        ),
    )
