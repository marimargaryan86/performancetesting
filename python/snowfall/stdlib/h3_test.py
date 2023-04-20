import zoneinfo
from typing import Collection

import pytest

from snowfall.stdlib import h3
from snowfall.stdlib.v1alpha import latlng_pb2

_H3_LOCATIONS = [
    h3.CoordinatesItem(
        identifier="SAT_IT_MA_XZWAD",
        latitude=46.287961,
        longitude=11.232652,
        timezone=zoneinfo.ZoneInfo("Europe/Stockholm"),
    ),
    h3.CoordinatesItem(
        identifier="SAT_DE_VO_XSTMO",
        latitude=49.2556226,
        longitude=6.8588948,
        timezone=zoneinfo.ZoneInfo("Europe/Stockholm"),
    ),
    h3.CoordinatesItem(
        identifier="SAT_FR_PA_WXNGQ",
        latitude=48.861496,
        longitude=2.33368,
        timezone=zoneinfo.ZoneInfo("Europe/Stockholm"),
    ),
    h3.CoordinatesItem(
        identifier="SAT_FR_RE_VDQTY",
        latitude=48.103175,
        longitude=-1.672335,
        timezone=zoneinfo.ZoneInfo("Europe/Stockholm"),
    ),
]


@pytest.fixture()
def h3_mapping_repository() -> h3.H3MappingRepository[h3.CoordinatesItem]:
    return h3.H3MappingRepository(
        mapping=_H3_LOCATIONS,
        resolution=8,
    )


@pytest.mark.parametrize(
    ("coordinates", "radius", "expected_station_ids"),
    [
        (
            latlng_pb2.LatLng(
                latitude=46.287961,
                longitude=11.232652,
            ),
            0,
            {"SAT_IT_MA_XZWAD"},
        ),
        (
            latlng_pb2.LatLng(
                latitude=59.638408,
                longitude=17.946854,
            ),
            0,
            set(),
        ),
        (
            latlng_pb2.LatLng(
                latitude=49.2556226,
                longitude=6.8588948,
            ),
            1,
            {"SAT_DE_VO_XSTMO"},
        ),
        (
            latlng_pb2.LatLng(
                latitude=48.861496,
                longitude=2.33368,
            ),
            1,
            {"SAT_FR_PA_WXNGQ"},
        ),
        (
            latlng_pb2.LatLng(
                latitude=48.103175,
                longitude=-1.672335,
            ),
            1,
            {"SAT_FR_RE_VDQTY"},
        ),
    ],
)
def test_coordinates_to_id(
    h3_mapping_repository: h3.H3MappingRepository[h3.CoordinatesItem],
    coordinates: latlng_pb2.LatLng,
    radius: int,
    expected_station_ids: Collection[str],
) -> None:
    assert expected_station_ids == {
        location.identifier
        for location in h3_mapping_repository.find_mapped_values(
            coordinates=coordinates,
            neighbour_search_radius=radius,
        )
    }
