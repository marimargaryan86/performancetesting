from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.v1 import latlng_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Location:
        """Fetch a location resource."""

    @abc.abstractmethod
    async def find(
        self,
        identifiers: Sequence[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> places_pb2.ListLocationsResponse:
        """Fetch all location resources."""

    @abc.abstractmethod
    async def get_nearby_locations(
        self,
        coordinates: latlng_pb2.LatLng,
    ) -> models_pb2.Location:
        """Fetch all nearby locations."""


class DictClient(Client):
    def __init__(self, locations: Sequence[models_pb2.Location]):
        self._locations = {location.id: location for location in locations}

    async def get(self, location_id: str) -> models_pb2.Location:
        try:
            return self._locations[location_id]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def find(
        self,
        identifiers: Sequence[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> places_pb2.ListLocationsResponse:
        all_locations = list(self._locations.values())

        if identifiers:
            all_locations = [
                location for location in all_locations if location.id in identifiers
            ]

        page = sequence.paginate(
            sequence=all_locations,
            cursor=cursor,
            limit=limit,
        )

        return places_pb2.ListLocationsResponse(
            locations=page.sequence,
            next_page_token=page.cursor,
        )

    async def get_nearby_locations(
        self,
        coordinates: latlng_pb2.LatLng,
    ) -> models_pb2.Location:
        return models_pb2.Location()


class GrpcClient(Client):
    def __init__(
        self,
        locations: places_pb2_grpc.LocationsServiceStub,
        timeout: int = 10,
    ):
        self._locations = locations
        self._timeout = timeout

    async def get(self, location_id: str) -> models_pb2.Location:
        response = await errors.handle_grpc_errors(
            self._locations.GetLocation(
                places_pb2.GetLocationRequest(id=location_id),
                timeout=self._timeout,
            ),
        )

        return response.location

    async def find(
        self,
        identifiers: Sequence[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> places_pb2.ListLocationsResponse:
        # TODO: handle INVALID_ARGUMENT
        request = places_pb2.ListLocationsRequest(
            page_token=cursor or "",
            ids=models_pb2.ListOfIds(ids=identifiers or []),
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._locations.ListLocations(request, timeout=self._timeout),
        )

    async def get_nearby_locations(
        self,
        coordinates: latlng_pb2.LatLng,
    ) -> models_pb2.Location:
        response = await errors.handle_grpc_errors(
            self._locations.ListNearbyLocations(
                request=places_pb2.ListNearbyLocationsRequest(coordinates=coordinates),
                timeout=self._timeout,
            ),
        )

        return response.locations
