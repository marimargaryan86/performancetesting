from unittest import mock

import grpc
import pytest

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, locations
from snowfall.project.junction.go.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)


class TestDictClient(object):
    async def test_single_location_is_retrievable(
        self,
        locations_client: locations.Client,
    ) -> None:
        location = await locations_client.get(fixtures.LOCATIONS[0])
        assert location.id == fixtures.LOCATIONS[0]

    async def test_missing_location_throws_error(
        self,
        locations_client: locations.Client,
    ) -> None:
        with pytest.raises(errors.NotFoundError):
            await locations_client.get(fixtures.NOT_FOUND)

    async def test_multiple_locations_are_retrievable(
        self,
        locations_client: locations.Client,
    ) -> None:
        found_locations = await locations_client.find(limit=100)
        assert len(found_locations.locations) == 2
        found_locations = await locations_client.find(limit=1)
        assert len(found_locations.locations) == 1

    async def test_multiple_filtered_locations_are_retrievable(
        self,
        locations_client: locations.Client,
    ) -> None:
        found_locations = await locations_client.find(
            identifiers=[fixtures.LOCATIONS[0]],
            limit=100,
        )
        assert len(found_locations.locations) == 1


class TestGrpcClient(object):
    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.UnhandledError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: type[Exception],
    ) -> None:
        stub = mock.create_autospec(places_pb2_grpc.LocationsServiceStub)
        stub.GetLocation = mock.AsyncMock(side_effect=error)
        client = locations.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_location_is_retrievable(self) -> None:
        proto = models_pb2.Location(id=fixtures.LOCATIONS[0])
        stub = mock.create_autospec(places_pb2_grpc.LocationsServiceStub)
        stub.GetLocation = mock.AsyncMock(
            return_value=places_pb2.GetLocationResponse(location=proto),
        )
        client = locations.GrpcClient(stub)
        location = await client.get(fixtures.LOCATIONS[0])
        assert location.id == fixtures.LOCATIONS[0]

    async def test_multiple_places_are_retrievable(self) -> None:
        response = places_pb2.ListLocationsResponse(
            locations=[
                models_pb2.Location(id=fixtures.LOCATIONS[0]),
                models_pb2.Location(id=fixtures.LOCATIONS[1]),
            ],
        )
        stub = mock.create_autospec(places_pb2_grpc.LocationsServiceStub)
        stub.ListLocations = mock.AsyncMock(return_value=response)
        client = locations.GrpcClient(stub)
        found_locations = await client.find(limit=100)
        assert len(found_locations.locations) == 2
