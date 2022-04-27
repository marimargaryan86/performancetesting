from typing import Sequence
from unittest import mock

import pytest

from snowfall.common.v1alpha import datetime_pb2
from snowfall.junction.providers.save_a_train import criteria, h3, train_stations
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc

_MOCK_STATIONS_MAPPING = (
    {
        "station_id": "SAT_DE_VO_XSTMO",
        "station_name": "Volklingen",
        "coordinates": "49.2556226,6.8588948",
    },
    {
        "station_id": "SAT_IT_MA_XZWAD",
        "station_name": "Magre Cortaccia",
        "coordinates": "46.287961,11.232652",
    },
    {
        "station_id": "SAT_FR_PA_WXNGQ",
        "station_name": "Paris All Stations",
        "coordinates": "48.861496,2.33368",
    },
    {
        "station_id": "SAT_FR_RE_VDQTY",
        "station_name": "Rennes",
        "coordinates": "48.103175,-1.672335",
    },
)


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture
async def train_stations_repository(
    mock_stations: Sequence[train_stations.TrainStation],
) -> train_stations.TrainStationRepository:
    return train_stations.TrainStationRepository(
        train_stations=mock_stations,
    )


@pytest.fixture
def h3_mapping_repository(
    mock_stations: Sequence[train_stations.TrainStation],
) -> h3.H3MappingRepository[train_stations.TrainStation]:
    return h3.H3MappingRepository[train_stations.TrainStation](
        mapping=train_stations.create_train_stations_mapping(
            train_stations=mock_stations,
        ),
        resolution=8,
    )


@pytest.fixture
def criteria_generator(
    h3_mapping_repository: h3.H3MappingRepository[train_stations.TrainStation],
) -> criteria.CriteriaGenerator:
    return criteria.CriteriaGenerator(h3_mapping=h3_mapping_repository)


@pytest.fixture
async def mock_stations() -> Sequence[train_stations.TrainStation]:
    stub = mock.create_autospec(geocoding_pb2_grpc.GeocodingServiceStub)
    stub.TimeZoneLookup = mock.AsyncMock(
        return_value=geocoding_pb2.TimeZoneLookupResponse(
            time_zone=datetime_pb2.TimeZone(
                id="America/Los_Angeles",
            ),
        ),
    )
    return [
        await train_stations.make_train_station(station, stub)
        for station in _MOCK_STATIONS_MAPPING
    ]
