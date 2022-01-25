from __future__ import annotations

import abc
import dataclasses
import random
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
    name: str
    latitude: float
    longitude: float
    country_code: str
    time_zone: str
    proto: Optional[models_pb2.Place] = None

    @classmethod
    async def from_proto(cls, grpc_place: models_pb2.Place) -> Place:
        return cls(
            country_code=grpc_place.country_code,
            identifier=uuid.UUID(grpc_place.id),
            latitude=grpc_place.latitude,
            longitude=grpc_place.longitude,
            name=grpc_place.name,
            proto=grpc_place,
            time_zone=grpc_place.time_zone,
        )


@dataclasses.dataclass(frozen=True)
class PlacesPage(object):
    places: Sequence[Place]
    next_page_token: Optional[str] = None

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
    async def find(self, limit: int, cursor: Optional[str] = None) -> PlacesPage:
        """Fetch all place resources."""


_LATITUDE_RANGE = (-90, 90)
_LONGITUDE_RANGE = (-180, 180)


class DictClient(Client):
    def __init__(self, places: Sequence[Mapping[str, Any]]):
        self._places = {
            place["id"]: Place(
                identifier=uuid.UUID(place["id"]),
                name="Foobar",
                latitude=random.uniform(*_LATITUDE_RANGE),  # nosec
                longitude=random.uniform(*_LONGITUDE_RANGE),  # nosec
                country_code="SE",
                time_zone="Europe/Stockholm",
            )
            for place in places
        }

    async def get(self, place_id: uuid.UUID) -> Place:
        try:
            return self._places[str(place_id)]
        except KeyError:
            raise NotFoundError("Place with ID '{id}' not found.".format(id=place_id))

    async def find(self, limit: int, cursor: Optional[str] = None) -> PlacesPage:
        return PlacesPage(places=list(self._places.values()))


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

    async def find(self, limit: int, cursor: Optional[str] = None) -> PlacesPage:
        # todo: handle INVALID_ARGUMENT
        response = await self._places.ListPlaces(  # type: ignore[misc]
            places_pb2.ListPlacesRequest(
                page_size=limit,
                page_token=cursor or "",
            ),
        )

        return await PlacesPage.from_proto(response)
