import collections
import dataclasses
import itertools
from typing import Generic, Sequence, TypeVar

from h3.api import numpy_int as h3

from snowfall.stdlib.v1alpha import models_pb2

_MappedValue = TypeVar("_MappedValue")


@dataclasses.dataclass(frozen=True)
class CoordinatesItem(Generic[_MappedValue]):
    latitude: float
    longitude: float
    mapped_value: _MappedValue


class H3MappingRepository(Generic[_MappedValue]):
    def __init__(
        self,
        mapping: Sequence[CoordinatesItem[_MappedValue]],
        resolution: int,
    ):
        # For a good resolution, see https://h3geo.org/docs/core-library/restable/
        self._resolution = resolution
        self._mapping: dict[int, list[_MappedValue]] = collections.defaultdict(list)

        for coordinates_item in mapping:
            self._mapping[
                h3.geo_to_h3(
                    coordinates_item.latitude,
                    coordinates_item.longitude,
                    self._resolution,
                )
            ].append(coordinates_item.mapped_value)

    def find_mapped_values(
        self,
        coordinates: models_pb2.Coordinates,
        neighbour_search_radius: int = 0,
    ) -> set[_MappedValue]:
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
