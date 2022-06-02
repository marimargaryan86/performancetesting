from __future__ import annotations

import abc
import dataclasses
from typing import Optional, Sequence

import grpc

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.places.v1alpha import places_pb2, places_pb2_grpc


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
    async def get(self, identifier: str) -> models_pb2.Place:
        """Fetch a place resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> PlacesPage:
        """Fetch all place resources."""


class DictClient(Client):
    def __init__(self, places: Sequence[models_pb2.Place]):
        self._places = {place.id: place for place in places}

    async def get(self, place_id: str) -> models_pb2.Place:
        try:
            return self._places[place_id]
        except KeyError as err:
            raise NotFoundError(
                "Place with ID '{id}' not found.".format(id=place_id),
            ) from err

    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> PlacesPage:
        return PlacesPage(places=list(self._places.values()))


class GrpcClient(Client):
    def __init__(self, places: places_pb2_grpc.PlacesServiceStub, timeout: int = 10):
        self._places = places
        self._timeout = timeout

    async def get(self, place_id: str) -> models_pb2.Place:
        try:
            response = await self._places.GetPlace(
                places_pb2.GetPlaceRequest(id=place_id),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Place with ID '{id}' not found.".format(id=place_id),
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
