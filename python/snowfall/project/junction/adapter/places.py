from __future__ import annotations

import abc
import dataclasses
from typing import Optional, Sequence

import grpc

from snowfall.project.junction.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib import sequence, string

_PLACE_NOT_FOUND_FROMAT = "Place with ID '{id}' not found."


class NotFoundError(Exception):
    """Raised when a place is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class PlacesPage(object):
    places: Sequence[models_pb2.Place]
    next_page_token: str = ""

    @classmethod
    async def from_proto(cls, grpc_places: places_pb2.ListPlacesResponse) -> PlacesPage:
        return cls(
            places=grpc_places.places,
            next_page_token=grpc_places.next_page_token,
        )


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(self, place: models_pb2.Place) -> models_pb2.Place:
        """Create a place resource."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Place:
        """Fetch a place resource."""

    @abc.abstractmethod
    async def delete(self, identifier: str) -> None:
        """Delete a place resource."""

    @abc.abstractmethod
    async def update(self, place: models_pb2.Place) -> models_pb2.Place:
        """Update a place resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> PlacesPage:
        """Fetch all place resources."""


class DictClient(Client):
    def __init__(self, places: Sequence[models_pb2.Place]):
        self._places = {place.location.id: place for place in places}

    async def create(self, place: models_pb2.Place) -> models_pb2.Place:
        new_place = models_pb2.Place()
        new_place.CopyFrom(place)
        new_place.location.id = string.uuid()
        self._places[new_place.location.id] = new_place

        return new_place

    async def get(self, place_id: str) -> models_pb2.Place:
        try:
            return self._places[place_id]
        except KeyError as err:
            raise NotFoundError(
                _PLACE_NOT_FOUND_FROMAT.format(id=place_id),
            ) from err

    async def delete(self, place_id: str) -> None:
        try:
            self._places.pop(place_id)
        except KeyError as err:
            raise NotFoundError(
                _PLACE_NOT_FOUND_FROMAT.format(id=place_id),
            ) from err

    async def update(self, place: models_pb2.Place) -> models_pb2.Place:
        self._places[place.location.id] = place

        return place

    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> PlacesPage:
        page = sequence.paginate(
            sequence=list(self._places.values()),
            cursor=cursor,
            limit=limit,
        )

        return PlacesPage(places=page.sequence, next_page_token=page.cursor)


class GrpcClient(Client):
    def __init__(self, places: places_pb2_grpc.PlacesServiceStub, timeout: int = 10):
        self._places = places
        self._timeout = timeout

    async def create(self, place: models_pb2.Place) -> models_pb2.Place:
        response = await self._places.CreatePlace(
            places_pb2.CreatePlaceRequest(
                place=place,
            ),
        )

        return response.place

    async def get(self, place_id: str) -> models_pb2.Place:
        try:
            response = await self._places.GetPlace(
                places_pb2.GetPlaceRequest(id=place_id),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    _PLACE_NOT_FOUND_FROMAT.format(id=place_id),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.place

    async def delete(self, identifier: str) -> None:
        try:
            await self._places.DeletePlace(
                places_pb2.DeletePlaceRequest(id=identifier),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    _PLACE_NOT_FOUND_FROMAT.format(id=identifier),
                ) from exc

            raise UnknownError(exc.details()) from exc

    async def update(self, place: models_pb2.Place) -> models_pb2.Place:
        try:
            response = await self._places.UpdatePlace(
                places_pb2.UpdatePlaceRequest(
                    place=place,
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    _PLACE_NOT_FOUND_FROMAT.format(id=place.location.id),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.place

    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> PlacesPage:
        # todo: handle INVALID_ARGUMENT
        request = places_pb2.ListPlacesRequest(
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        response = await self._places.ListPlaces(request, timeout=self._timeout)

        return await PlacesPage.from_proto(response)
