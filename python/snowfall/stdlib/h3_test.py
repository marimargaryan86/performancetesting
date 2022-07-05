from typing import Collection

import pytest

from snowfall.fixtures import H3LocationTestModel
from snowfall.stdlib import h3
from snowfall.stdlib.v1alpha import models_pb2


@pytest.mark.parametrize(
    "coordinates, radius, expected_station_ids",
    [
        (
            models_pb2.Coordinates(
                latitude=46.287961,
                longitude=11.232652,
            ),
            0,
            {"SAT_IT_MA_XZWAD"},
        ),
        (
            models_pb2.Coordinates(
                latitude=59.638408,
                longitude=17.946854,
            ),
            0,
            set(),
        ),
        (
            models_pb2.Coordinates(
                latitude=49.2556226,
                longitude=6.8588948,
            ),
            1,
            {"SAT_DE_VO_XSTMO"},
        ),
        (
            models_pb2.Coordinates(
                latitude=48.861496,
                longitude=2.33368,
            ),
            1,
            {"SAT_FR_PA_WXNGQ"},
        ),
        (
            models_pb2.Coordinates(
                latitude=48.103175,
                longitude=-1.672335,
            ),
            1,
            {"SAT_FR_RE_VDQTY"},
        ),
    ],
)
def test_coordinates_to_id(
    h3_mapping_repository: h3.H3MappingRepository[H3LocationTestModel],
    coordinates: models_pb2.Coordinates,
    radius: int,
    expected_station_ids: Collection[str],
) -> None:
    assert expected_station_ids == {
        location.id_
        for location in h3_mapping_repository.find_mapped_values(
            coordinates=coordinates,
            neighbour_search_radius=radius,
        )
    }
