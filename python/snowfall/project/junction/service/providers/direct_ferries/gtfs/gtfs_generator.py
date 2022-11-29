import csv
import enum
import os
import zipfile
from typing import Generator, Optional, Sequence

import orjson
import pydantic

from snowfall.project.junction.service.providers.direct_ferries.gtfs import (
    converter as gtfs_converter,
)

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
    latitude: Optional[float]
    longitude: Optional[float]


class RouteMapping(pydantic.BaseModel):
    route_id: str
    origin: Optional[str]
    destination: Optional[str]


def _models_to_csv(
    file_name: str,
    models: Generator[pydantic.BaseModel, None, None],
) -> str:
    with open(file_name, _WRITE_MODE) as file_obj:
        first = next(models)

        writer = csv.DictWriter(
            file_obj,
            fieldnames=first.schema()[_CLASS_PROPERTIES].keys(),
        )

        writer.writeheader()
        writer.writerow(orjson.loads(first.json()))
        writer.writerows(orjson.loads(data_item.json()) for data_item in models)

    return file_name


class GTFSGenerator(object):
    async def generate_feed(
        self,
        converter: gtfs_converter.DFDataConverter,
    ) -> None:
        _models_to_csv(CompressFileList.agency.value, converter.convert_agency())
        _models_to_csv(CompressFileList.feed_info.value, converter.convert_feed_info())
        _models_to_csv(CompressFileList.stops.value, converter.convert_stops())
        _models_to_csv(CompressFileList.routes.value, converter.convert_routes())
        _models_to_csv(CompressFileList.trips.value, converter.convert_trips())
        _models_to_csv(
            CompressFileList.stop_times.value,
            converter.convert_stop_times(),
        )
        _models_to_csv(
            CompressFileList.calendar_dates.value,
            converter.convert_calendar_dates(),
        )

        self.compress_files()

    def compress_files(self) -> None:
        with zipfile.ZipFile(
            "{0}/df_schedules.zip".format(_OUTPUT_PATH),
            "w",
        ) as zip_f:
            for file_name in CompressFileList.file_list():
                zip_f.write(file_name, compress_type=zipfile.ZIP_DEFLATED)
                os.remove(file_name)
