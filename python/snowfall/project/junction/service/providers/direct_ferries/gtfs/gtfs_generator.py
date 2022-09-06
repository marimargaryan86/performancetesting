import csv
import enum
import os
import zipfile
from typing import Optional, Sequence

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
    transfers = "transfers.txt"

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


class GTFSGenerator(object):
    async def generate_feed(  # noqa: WPS210
        self,
        converter: gtfs_converter.DFDataConverter,
    ) -> None:
        agency = converter.convert_agency()
        feed_info = converter.convert_feed_info()
        stops = converter.convert_stops()
        routes = converter.convert_routes()
        trips = converter.convert_trips()
        stop_times = converter.convert_stop_times()
        calendar_dates = converter.convert_calendar_dates()
        transfers = converter.convert_transfers()

        self.prepare_file(CompressFileList.agency, agency)
        self.prepare_file(CompressFileList.feed_info, feed_info)
        self.prepare_file(CompressFileList.stops, stops)
        self.prepare_file(CompressFileList.routes, routes)
        self.prepare_file(CompressFileList.trips, trips)
        self.prepare_file(CompressFileList.stop_times, stop_times)
        self.prepare_file(CompressFileList.calendar_dates, calendar_dates)
        self.prepare_file(CompressFileList.transfers, transfers)
        self.compress_files()

    def prepare_file(
        self,
        file_name: CompressFileList,
        gtfs_data: Sequence[pydantic.BaseModel],
    ) -> None:
        with open(file_name.value, _WRITE_MODE) as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=gtfs_data[0].schema()[_CLASS_PROPERTIES].keys(),
            )
            writer.writeheader()
            for data_item in gtfs_data:
                file_item = data_item.dict()
                writer.writerow(file_item)

    def compress_files(self) -> None:
        with zipfile.ZipFile(
            "{0}/df_schedules.zip".format(_OUTPUT_PATH),
            "w",
        ) as zip_f:
            for file_name in CompressFileList.file_list():
                zip_f.write(file_name, compress_type=zipfile.ZIP_DEFLATED)
                os.remove(file_name)
