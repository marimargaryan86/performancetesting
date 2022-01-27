import uuid
from typing import Type
from unittest import mock

import grpc
import pytest

from snowfall.adapter import places
from snowfall.common.v1alpha import models_pb2
from snowfall.conftest import PLACE_NOT_FOUND, PLACES
from snowfall.junction.places.v1alpha import places_pb2, places_pb2_grpc


@pytest.mark.asyncio
class TestDictClient(object):
    async def test_single_place_is_retrievable(
        self,
        places_client: places.Client,
    ) -> None:
        identifier = PLACES[0]["id"]
        place = await places_client.get(uuid.UUID(identifier))
        assert str(place.identifier) == identifier

    async def test_missing_place_throws_error(
        self,
        places_client: places.Client,
    ) -> None:
        with pytest.raises(places.NotFoundError):
            await places_client.get(uuid.UUID(PLACE_NOT_FOUND))

    async def test_multiple_places_are_retrievable(
        self,
        places_client: places.Client,
    ) -> None:
        found_places = await places_client.find(limit=100)
        assert len(found_places.places) == 2


@pytest.mark.asyncio
class TestGrpcClient(object):
    @pytest.mark.parametrize(
        "error, expected",
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                places.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                places.UnknownError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: Type[Exception],
    ) -> None:
        stub = mock.create_autospec(places_pb2_grpc.PlacesServiceStub)
        stub.GetPlace = mock.AsyncMock(side_effect=error)
        client = places.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(uuid.UUID(PLACE_NOT_FOUND))

    async def test_single_place_is_retrievable(self) -> None:
        identifier = PLACES[0]["id"]
        proto = models_pb2.Place(id=identifier)
        stub = mock.create_autospec(places_pb2_grpc.PlacesServiceStub)
        stub.GetPlace = mock.AsyncMock(
            return_value=places_pb2.GetPlaceResponse(place=proto),
        )
        client = places.GrpcClient(stub)
        place = await client.get(uuid.UUID(identifier))
        assert str(place.identifier) == identifier
        assert place.proto == proto

    async def test_multiple_places_are_retrievable(self) -> None:
        response = places_pb2.ListPlacesResponse(
            places=[
                models_pb2.Place(id=PLACES[0]["id"]),
                models_pb2.Place(id=PLACES[1]["id"]),
            ],
        )
        stub = mock.create_autospec(places_pb2_grpc.PlacesServiceStub)
        stub.ListPlaces = mock.AsyncMock(return_value=response)
        client = places.GrpcClient(stub)
        found_places = await client.find(limit=100)
        assert len(found_places.places) == 2
