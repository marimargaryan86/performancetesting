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
from snowfall.stdlib import sequence


class NotFoundError(Exception):
    """Raised when a location is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class LocationsPage(object):
    locations: Sequence[models_pb2.Location]
    next_page_token: str = ""

    @classmethod
    async def from_proto(
        cls,
        grpc_locations: places_pb2.ListLocationsResponse,
    ) -> LocationsPage:
        return cls(
            locations=grpc_locations.locations,
            next_page_token=grpc_locations.next_page_token,
        )


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Location:
        """Fetch a location resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> LocationsPage:
        """Fetch all location resources."""


class DictClient(Client):
    def __init__(self, locations: Sequence[models_pb2.Location]):
        self._locations = {location.id: location for location in locations}

    async def get(self, location_id: str) -> models_pb2.Location:
        try:
            return self._locations[location_id]
        except KeyError as err:
            raise NotFoundError(
                "Location with ID '{id}' not found.".format(id=location_id),
            ) from err

    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> LocationsPage:
        page = sequence.paginate(
            sequence=list(self._locations.values()),
            cursor=cursor,
            limit=limit,
        )

        return LocationsPage(locations=page.sequence, next_page_token=page.cursor)


class GrpcClient(Client):
    def __init__(
        self,
        locations: places_pb2_grpc.LocationsServiceStub,
        timeout: int = 10,
    ):
        self._locations = locations
        self._timeout = timeout

    async def get(self, location_id: str) -> models_pb2.Location:
        try:
            response = await self._locations.GetLocation(
                places_pb2.GetLocationRequest(id=location_id),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Location with ID '{id}' not found.".format(id=location_id),
                ) from exc

            raise UnknownError(exc.details()) from exc

        return response.location

    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> LocationsPage:
        # todo: handle INVALID_ARGUMENT
        request = places_pb2.ListLocationsRequest(
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        response = await self._locations.ListLocations(request, timeout=self._timeout)

        return await LocationsPage.from_proto(response)
