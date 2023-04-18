from unittest import mock

import grpc
import pytest

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, places
from snowfall.project.junction.go.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)


class TestDictClient(object):
    async def test_single_place_is_retrievable(
        self,
        places_client: places.Client,
    ) -> None:
        place = await places_client.get(fixtures.PLACES[0])
        assert place.location.id == fixtures.PLACES[0]

    async def test_missing_place_throws_error(
        self,
        places_client: places.Client,
    ) -> None:
        with pytest.raises(errors.NotFoundError):
            await places_client.get(fixtures.NOT_FOUND)

    async def test_multiple_places_are_retrievable(
        self,
        places_client: places.Client,
    ) -> None:
        found_places = await places_client.find(limit=100)
        assert len(found_places.places) == 2

    async def test_single_place_is_creatable(
        self,
        places_client: places.Client,
    ) -> None:
        place = await places_client.get(fixtures.PLACES[0])
        place = await places_client.create(place)
        new_place = await places_client.get(place.location.id)
        assert place.location.id == new_place.location.id


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
        stub = mock.create_autospec(places_pb2_grpc.PlacesServiceStub)
        stub.GetPlace = mock.AsyncMock(side_effect=error)
        client = places.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_place_is_retrievable(self) -> None:
        proto = models_pb2.Place(location=models_pb2.Location(id=fixtures.PLACES[0]))
        stub = mock.create_autospec(places_pb2_grpc.PlacesServiceStub)
        stub.GetPlace = mock.AsyncMock(
            return_value=places_pb2.GetPlaceResponse(place=proto),
        )
        client = places.GrpcClient(stub)
        place = await client.get(fixtures.PLACES[0])
        assert place.location.id == fixtures.PLACES[0]

    async def test_multiple_places_are_retrievable(self) -> None:
        response = places_pb2.ListPlacesResponse(
            places=[
                models_pb2.Place(location=models_pb2.Location(id=fixtures.PLACES[0])),
                models_pb2.Place(location=models_pb2.Location(id=fixtures.PLACES[1])),
            ],
        )
        stub = mock.create_autospec(places_pb2_grpc.PlacesServiceStub)
        stub.ListPlaces = mock.AsyncMock(return_value=response)
        client = places.GrpcClient(stub)
        found_places = await client.find(limit=100)
        assert len(found_places.places) == 2
