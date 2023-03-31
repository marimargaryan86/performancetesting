import uuid

from grpc import StatusCode, aio

from snowfall.project.junction.service.places import places
from snowfall.project.junction.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service

_MAX_DISTANCE_AIRPORT = 50000
_MAX_DISTANCE_RAIL_STATION = 10000


class LocationsService(service.Service, places_pb2_grpc.LocationsServiceServicer):
    def __init__(self, locations: places.LocationRepository, default_page_size: int):
        self._default_page_size = default_page_size
        self._locations = locations

    def get_name(self) -> str:
        return places_pb2.DESCRIPTOR.services_by_name["LocationsService"].full_name

    def register(self, server: aio.Server) -> None:
        places_pb2_grpc.add_LocationsServiceServicer_to_server(self, server)

    async def GetLocation(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.GetLocationRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetLocationResponse:
        location = await self._locations.find_by_id(request.id)

        if not location:
            await context.abort(StatusCode.NOT_FOUND)

        if location and not location.types:  # TODO: not needed with NoReturn above.
            location.types.append(models_pb2.Location.TYPE_UNSPECIFIED)

        return places_pb2.GetLocationResponse(location=location)

    async def ListLocations(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.ListLocationsRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListLocationsResponse:
        locations_result = await self._locations.find(
            cursor=request.page_token,
            identifiers=list(request.ids.ids) if request.HasField("ids") else None,
        )

        locations_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        locations = []

        async for location in locations_result:
            if not location.types:
                location.types.append(models_pb2.Location.TYPE_UNSPECIFIED)

            locations.append(location)

        return places_pb2.ListLocationsResponse(
            locations=locations,
            next_page_token=await locations_result.cursor(),
        )

    async def ListNearbyLocations(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.ListNearbyLocationsRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListNearbyLocationsResponse:
        return places_pb2.ListNearbyLocationsResponse(
            locations=await self._locations.find_within_area_per_type(
                cursor="",
                filter_=places.FindPlacesPerAreaFilter(
                    latitude=float(request.coordinates.latitude),
                    longitude=float(request.coordinates.longitude),
                    type_distances=[
                        places.PlaceTypeDistancePair(
                            max_distance_meters=_MAX_DISTANCE_AIRPORT,
                            location_type=models_pb2.Location.Type.TYPE_AIRPORT,
                        ),
                        places.PlaceTypeDistancePair(
                            max_distance_meters=_MAX_DISTANCE_RAIL_STATION,
                            location_type=models_pb2.Location.Type.TYPE_RAILWAY_STATION,
                        ),
                    ],
                ),
            ),
        )


class PlacesService(  # noqa: WPS214
    service.Service,
    places_pb2_grpc.PlacesServiceServicer,
):
    def __init__(
        self,
        places_repository: places.PlaceRepository,
        default_page_size: int,
    ):
        self._default_page_size = default_page_size
        self._places = places_repository

    def get_name(self) -> str:
        return places_pb2.DESCRIPTOR.services_by_name["PlacesService"].full_name

    def register(self, server: aio.Server) -> None:
        places_pb2_grpc.add_PlacesServiceServicer_to_server(self, server)

    async def GetPlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.GetPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceResponse:
        try:
            uuid.UUID(request.id)
        except ValueError:
            await context.abort(StatusCode.INVALID_ARGUMENT)

        place_result = await self._places.find_by_id(request.id)

        if not place_result:
            await context.abort(StatusCode.NOT_FOUND)

        return places_pb2.GetPlaceResponse(place=place_result)

    async def ListPlaces(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.ListPlacesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListPlacesResponse:
        places_result = await self._places.find(request.page_token)

        places_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return places_pb2.ListPlacesResponse(
            places=[place async for place in places_result],
            next_page_token=await places_result.cursor(),
        )

    async def CreatePlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.CreatePlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.CreatePlaceResponse:
        await self._places.create(request.place)

        return places_pb2.CreatePlaceResponse(
            place=request.place,
        )

    async def DeletePlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.DeletePlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.DeletePlaceResponse:
        try:
            uuid.UUID(request.id)
        except ValueError:
            await context.abort(StatusCode.INVALID_ARGUMENT)

        await self._places.delete(request.id)

        return places_pb2.DeletePlaceResponse()

    async def UpdatePlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.UpdatePlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.UpdatePlaceResponse:
        await self._places.update(request.place)

        return places_pb2.UpdatePlaceResponse(
            place=request.place,
        )
