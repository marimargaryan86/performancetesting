import pathlib
import zipfile
from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from snowfall.project.junction.service.routes.v1 import stops_pb2
from snowfall.project.junction.v1 import stop_type_pb2
from snowfall.stdlib import string
from snowfall.stdlib.v1 import latlng_pb2

_ROUTES = "routes.txt"
_TRIPS = "trips.txt"
_STOP_TIMES = "stop_times.txt"
_STOPS = "stops.txt"


class GtfsFile(object):
    def __init__(self, gtfs_file: zipfile.ZipFile, chunk_size: int = 100000):
        self._gtfs_file = gtfs_file
        self._chunk_size = chunk_size
        self._file_mapping = {
            zipfile.Path(gtfs_file, file_name).name: file_name
            for file_name in gtfs_file.namelist()
        }
        self._file_name = pathlib.Path(self._gtfs_file.filename or "unknown.zip").name
        self._source = string.to_uuid(self._file_name)

    def get_stops(self) -> Iterable[stops_pb2.Stop]:
        with pd.read_csv(
            self._gtfs_file.open(self._file_mapping[_STOPS]),
            engine="c",
            usecols=["stop_id", "stop_name", "stop_lat", "stop_lon"],
            chunksize=self._chunk_size,
        ) as reader:
            for chunk in reader:
                filtered_chunk = chunk[~chunk["stop_id"].str.startswith("stoparea")]
                yield from (
                    self._make_stop(row) for _, row in filtered_chunk.iterrows()
                )

    def _make_stop(self, stop: Mapping[str, Any]) -> stops_pb2.Stop:
        return stops_pb2.Stop(
            id=self._generate_uuid(stop["stop_id"]),
            source=self._source,
            source_ref=stop["stop_id"],
            name=stop["stop_name"],
            coordinates=latlng_pb2.LatLng(
                latitude=stop["stop_lat"],
                longitude=stop["stop_lon"],
            ),
            type=stop_type_pb2.STOP_TYPE_UNSPECIFIED,
            metadata=stops_pb2.Stop.Metadata(
                iata=stop["stop_id"] if len(stop["stop_id"]) == 3 else None,
            ),
        )

    def _generate_uuid(self, identifier: str) -> str:
        return string.to_uuid("{0}:{1}".format(identifier, self._file_name))
