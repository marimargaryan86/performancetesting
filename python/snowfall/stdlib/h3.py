import collections
import dataclasses
import itertools
import zoneinfo
from collections.abc import Iterable
from typing import Generic, TypeVar

from h3.api import numpy_int as h3

from snowfall.stdlib.v1 import latlng_pb2


@dataclasses.dataclass(frozen=True)
class CoordinatesItem(object):
    identifier: str
    latitude: float
    longitude: float
    timezone: zoneinfo.ZoneInfo


MappedValue = TypeVar("MappedValue", bound=CoordinatesItem)


class H3MappingRepository(Generic[MappedValue]):
    def __init__(
        self,
        mapping: Iterable[MappedValue],
        resolution: int,
    ):
        # For a good resolution, see https://h3geo.org/docs/core-library/restable/
        self._resolution = resolution
        self._mapping: dict[int, list[MappedValue]] = collections.defaultdict(list)

        for coordinates_item in mapping:
            self._mapping[
                h3.geo_to_h3(
                    coordinates_item.latitude,
                    coordinates_item.longitude,
                    self._resolution,
                )
            ].append(coordinates_item)

    def find_mapped_values(
        self,
        coordinates: latlng_pb2.LatLng,
        neighbour_search_radius: int = 0,
    ) -> set[MappedValue]:
        point_h3 = h3.geo_to_h3(
            coordinates.latitude,
            coordinates.longitude,
            self._resolution,
        )

        if neighbour_search_radius == 0 or self._mapping[point_h3]:
            return set(self._mapping[point_h3])

        area = [point_h3, *h3.k_ring(point_h3, neighbour_search_radius)]

        return set(
            itertools.chain.from_iterable(self._mapping[h3_id] for h3_id in area),
        )
