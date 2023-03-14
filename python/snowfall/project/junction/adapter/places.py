from __future__ import annotations

import abc
from typing import Sequence

from snowfall.project.junction.adapter import errors
from snowfall.project.junction.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib import sequence, string


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
        limit: int | None = None,
        cursor: str | None = None,
    ) -> places_pb2.ListPlacesResponse:
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
            raise errors.NotFoundError() from err

    async def delete(self, place_id: str) -> None:
        try:
            self._places.pop(place_id)
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def update(self, place: models_pb2.Place) -> models_pb2.Place:
        self._places[place.location.id] = place

        return place

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> places_pb2.ListPlacesResponse:
        page = sequence.paginate(
            sequence=list(self._places.values()),
            cursor=cursor,
            limit=limit,
        )

        return places_pb2.ListPlacesResponse(
            places=page.sequence,
            next_page_token=page.cursor,
        )


class GrpcClient(Client):
    def __init__(self, places: places_pb2_grpc.PlacesServiceStub, timeout: int = 10):
        self._places = places
        self._timeout = timeout

    async def create(self, place: models_pb2.Place) -> models_pb2.Place:
        response = await errors.handle_grpc_errors(
            self._places.CreatePlace(
                places_pb2.CreatePlaceRequest(
                    place=place,
                ),
            ),
        )

        return response.place

    async def get(self, place_id: str) -> models_pb2.Place:
        response = await errors.handle_grpc_errors(
            self._places.GetPlace(
                places_pb2.GetPlaceRequest(id=place_id),
                timeout=self._timeout,
            ),
        )

        return response.place

    async def delete(self, identifier: str) -> None:
        await errors.handle_grpc_errors(
            self._places.DeletePlace(
                places_pb2.DeletePlaceRequest(id=identifier),
                timeout=self._timeout,
            ),
        )

    async def update(self, place: models_pb2.Place) -> models_pb2.Place:
        response = await errors.handle_grpc_errors(
            self._places.UpdatePlace(
                places_pb2.UpdatePlaceRequest(
                    place=place,
                ),
                timeout=self._timeout,
            ),
        )

        return response.place

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> places_pb2.ListPlacesResponse:
        # todo: handle INVALID_ARGUMENT
        request = places_pb2.ListPlacesRequest(
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._places.ListPlaces(request, timeout=self._timeout),
        )
