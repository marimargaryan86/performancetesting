from __future__ import annotations

import abc
import dataclasses
import uuid
from typing import Any, Mapping, Optional, Sequence

import grpc

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.places.v1alpha import places_pb2, places_pb2_grpc


class NotFoundError(Exception):
    """Raised when a place is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class Place(object):
    identifier: uuid.UUID
    proto: Optional[models_pb2.Place] = None

    @classmethod
    async def from_proto(cls, grpc_place: models_pb2.Place) -> Place:
        return cls(identifier=uuid.UUID(grpc_place.id), proto=grpc_place)


@dataclasses.dataclass(frozen=True)
class PlacesPage(object):
    places: Sequence[Place]
    next_page_token: str

    @classmethod
    async def from_proto(cls, grpc_places: places_pb2.ListPlacesResponse) -> PlacesPage:
        return cls(
            places=[await Place.from_proto(place) for place in grpc_places.places],
            next_page_token=grpc_places.next_page_token,
        )


class Client(object):
    @abc.abstractmethod
    async def get(self, identifier: uuid.UUID) -> Place:
        """Fetch a place resource."""

    @abc.abstractmethod
    async def find(self) -> PlacesPage:
        """Fetch all place resources."""


class DictClient(Client):
    def __init__(self, places: Sequence[Mapping[str, Any]]):
        self._places = {
            place["id"]: Place(
                identifier=uuid.UUID(place["id"]),
            )
            for place in places
        }

    async def get(self, place_id: uuid.UUID) -> Place:
        try:
            return self._places[str(place_id)]
        except KeyError:
            raise NotFoundError("Place with ID '{id}' not found.".format(id=place_id))

    async def find(self) -> PlacesPage:
        next_page = "next_page"
        return PlacesPage(places=list(self._places.values()), next_page_token=next_page)


class GrpcClient(Client):
    def __init__(self, places: places_pb2_grpc.PlacesServiceStub):
        self._places = places

    async def get(self, place_id: uuid.UUID) -> Place:
        try:
            response = await self._places.GetPlace(  # type: ignore[misc]
                places_pb2.GetPlaceRequest(id=str(place_id)),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Place with ID '{id}' not found.".format(id=place_id),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return await Place.from_proto(response.place)

    async def find(self) -> PlacesPage:
        response = await self._places.ListPlaces(  # type: ignore[misc]
            places_pb2.ListPlacesRequest(),
        )

        return await PlacesPage.from_proto(response)
