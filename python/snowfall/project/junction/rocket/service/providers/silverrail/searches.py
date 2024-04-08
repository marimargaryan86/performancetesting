import functools
import zoneinfo
from collections.abc import Iterable

from geopy.distance import geodesic

from snowfall.project.junction.rocket.service.providers.silverrail import (
    criteria,
    train_stations,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.v1 import latlng_pb2


def _calculate_distance_geopy(
    p1: tuple[float, float],
    p2: train_stations.TrainStation,
) -> float:
    """Return the great circle distance in meters between two points using geopy."""
    station = (p2.latitude, p2.longitude)
    return geodesic(p1, station).meters


def _find_nearest_provider_place(
    stations: Iterable[train_stations.TrainStation],
    coordinates: latlng_pb2.LatLng,
) -> tuple[str, zoneinfo.ZoneInfo]:
    coords = coordinates.latitude, coordinates.longitude
    nearest_station = min(
        stations,
        key=functools.partial(_calculate_distance_geopy, coords),
    )

    return nearest_station.identifier, nearest_station.timezone


class CriteriaGenerator:
    def __init__(
        self,
        h3_mapping: h3.H3MappingRepository[train_stations.TrainStation],
    ):
        self._mapping = h3_mapping

    def criteria_task_generator(
        self,
        search: models_pb2.Search,
    ) -> list[criteria.Criteria]:
        # TODO(regis.blanc): use train stations in the criteria
        return criteria.search_criteria_generator(search)

    def _get_stations(
        self,
        coordinates: latlng_pb2.LatLng,
    ) -> set[train_stations.TrainStation]:
        self._mapping.find_mapped_values(
            coordinates=coordinates,
            neighbour_search_radius=1,
        )

        return self._mapping.find_mapped_values(
            coordinates=coordinates,
            neighbour_search_radius=1,
        )
