import uuid
from typing import Type
from unittest import mock

import grpc
import pytest

from snowfall.adapter import places
from snowfall.common.v1alpha import models_pb2
from snowfall.junction.places.v1alpha import places_pb2, places_pb2_grpc

_PLACE_NOT_FOUND = "f55b0ec5-7c87-4c35-86f4-1417a5f50e89"
_PLACES = (
    {"id": "f236a92c-4cfa-468e-85ef-431d25dcd925"},
    {"id": "488a836d-ec22-439b-a9d8-3c4c386a731e"},
)


@pytest.mark.asyncio
class TestDictClient(object):
    async def test_single_place_is_retrievable(self) -> None:
        client = places.DictClient(_PLACES)
        identifier = _PLACES[0]["id"]
        place = await client.get(uuid.UUID(identifier))
        assert str(place.identifier) == identifier

    async def test_missing_place_throws_error(self) -> None:
        client = places.DictClient(_PLACES)
        with pytest.raises(places.NotFoundError):
            await client.get(uuid.UUID(_PLACE_NOT_FOUND))

    async def test_multiple_places_are_retrievable(self) -> None:
        client = places.DictClient(_PLACES)
        found_places = await client.find()
        assert len(found_places.places) == 2
        assert str(found_places.places[0].identifier) == _PLACES[0]["id"]
        assert str(found_places.places[1].identifier) == _PLACES[1]["id"]


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
            await client.get(uuid.UUID(_PLACE_NOT_FOUND))

    async def test_single_place_is_retrievable(self) -> None:
        identifier = _PLACES[0]["id"]
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
                models_pb2.Place(id=_PLACES[0]["id"]),
                models_pb2.Place(id=_PLACES[1]["id"]),
            ],
        )
        stub = mock.create_autospec(places_pb2_grpc.PlacesServiceStub)
        stub.ListPlaces = mock.AsyncMock(return_value=response)
        client = places.GrpcClient(stub)
        found_places = await client.find()
        assert len(found_places.places) == 2
        assert str(found_places.places[0].identifier) == _PLACES[0]["id"]
        assert str(found_places.places[1].identifier) == _PLACES[1]["id"]
