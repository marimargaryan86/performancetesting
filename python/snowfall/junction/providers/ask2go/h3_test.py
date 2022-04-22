from typing import Collection

import pytest

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.providers.ask2go import airports, h3


@pytest.mark.parametrize(
    "coordinates, radius, expected_iatas",
    [
        (
            models_pb2.Coordinates(
                latitude=59.650831,
                longitude=17.92119,
            ),
            0,
            {"ARN"},
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
                latitude=59.638408,
                longitude=17.946854,
            ),
            1,
            {"ARN"},
        ),
        (
            models_pb2.Coordinates(
                latitude=51.470311,
                longitude=-0.458118,
            ),
            0,
            {"LHR"},
        ),
        (
            models_pb2.Coordinates(
                latitude=51.458069,
                longitude=-0.443896,
            ),
            1,
            {"LHR"},
        ),
        (
            models_pb2.Coordinates(
                latitude=26.470242,
                longitude=49.797683,
            ),
            1,
            {"DMM"},
        ),
        (
            models_pb2.Coordinates(
                latitude=5.811213,
                longitude=-55.190927,
            ),
            16,
            {"ORG"},
        ),
        (
            models_pb2.Coordinates(
                latitude=59.351209,
                longitude=-2.900537,
            ),
            1,
            {"PPW"},
        ),
        (
            models_pb2.Coordinates(
                latitude=59.350376,
                longitude=-2.949954,
            ),
            1,
            {"WRY"},
        ),
    ],
)
def test_coordinates_to_iata(
    h3_mapping_repository: h3.H3MappingRepository[airports.Airport],
    coordinates: models_pb2.Coordinates,
    radius: int,
    expected_iatas: Collection[str],
) -> None:
    assert expected_iatas == {
        airport.iata
        for airport in h3_mapping_repository.find_mapped_values(
            coordinates=coordinates,
            neighbour_search_radius=radius,
        )
    }
