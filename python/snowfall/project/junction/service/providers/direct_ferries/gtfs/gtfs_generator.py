import csv
import enum
import os
import zipfile
from collections.abc import Generator, Sequence

import orjson
import pydantic

from snowfall.project.junction.service.providers.direct_ferries.gtfs import (
    converter as gtfs_converter,
)
from snowfall.stdlib.format.gtfs import models as gtfs_models

_WRITE_MODE = "w"
_CLASS_PROPERTIES = "properties"
_OUTPUT_PATH = "dist/import/gtfs-feed/direct-ferries"
_CURRENT_DIRECTORY = (
    "python/snowfall/project/junction/service/providers/direct_ferries/gtfs"
)


class CompressFileList(enum.Enum):
    agency = "agency.txt"
    feed_info = "feed_info.txt"
    stops = "stops.txt"
    routes = "routes.txt"
    trips = "trips.txt"
    stop_times = "stop_times.txt"
    calendar_dates = "calendar_dates.txt"

    @classmethod
    def file_list(cls) -> Sequence[str]:
        return [file_name.value for file_name in cls]


class Place(pydantic.BaseModel):
    port_code: str
    latitude: float | None
    longitude: float | None


class RouteMapping(pydantic.BaseModel):
    route_id: str
    origin: str | None
    destination: str | None


def _models_to_csv(
    file_name: str,
    models: Generator[pydantic.BaseModel, None, None],
    model_class: type[pydantic.BaseModel],
) -> str:
    with open(file_name, _WRITE_MODE) as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=model_class.schema()[_CLASS_PROPERTIES].keys(),
        )

        writer.writeheader()
        writer.writerows(orjson.loads(data_item.json()) for data_item in models)

    return file_name


class GTFSGenerator(object):
    def __init__(self, output_dir: str) -> None:
        self._output_dir = output_dir

    async def generate_feed(
        self,
        converter: gtfs_converter.DFDataConverter,
    ) -> None:
        _models_to_csv(
            CompressFileList.agency.value,
            converter.convert_agency(),
            gtfs_models.Agency,
        )
        _models_to_csv(
            CompressFileList.feed_info.value,
            converter.convert_feed_info(),
            gtfs_models.FeedInfo,
        )
        _models_to_csv(
            CompressFileList.stops.value,
            converter.convert_stops(),
            gtfs_models.Stop,
        )
        _models_to_csv(
            CompressFileList.routes.value,
            converter.convert_routes(),
            gtfs_models.Route,
        )
        _models_to_csv(
            CompressFileList.trips.value,
            converter.convert_trips(),
            gtfs_models.Trip,
        )
        _models_to_csv(
            CompressFileList.stop_times.value,
            converter.convert_stop_times(),
            gtfs_models.StopTime,
        )
        _models_to_csv(
            CompressFileList.calendar_dates.value,
            converter.convert_calendar_dates(),
            gtfs_models.CalendarDate,
        )

        self.compress_files()

    def compress_files(self) -> None:
        with zipfile.ZipFile(
            "{0}/directferries.zip".format(self._output_dir),
            "w",
        ) as zip_f:
            for file_name in CompressFileList.file_list():
                zip_f.write(file_name, compress_type=zipfile.ZIP_DEFLATED)
                os.remove(file_name)
