from grpc import StatusCode, aio

from snowfall.project.junction.rocket.service.places import places
from snowfall.project.junction.rocket.service.places.v1alpha import (
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class PlacesService(
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

    async def GetPlace(  # type: ignore[override]  # noqa: N802
        self,
        request: places_pb2.GetPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceResponse:
        place = await self._places.find_by_id(document_id=request.id)
        if not place:
            await context.abort(
                code=StatusCode.NOT_FOUND,
            )
        return places_pb2.GetPlaceResponse(place=place)

    async def GetPlaceClosestToCoordinates(  # type: ignore[override]  # noqa: N802
        self,
        request: places_pb2.GetPlaceClosestToCoordinatesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceClosestToCoordinatesResponse:
        closest_place = await self._places.find_closest_within_radius(
            coordinates=request.coordinates_and_radius.coordinates,
            radius=request.coordinates_and_radius.radius,
        )
        if not closest_place:
            await context.abort(code=StatusCode.NOT_FOUND)
        return places_pb2.GetPlaceClosestToCoordinatesResponse(place=closest_place)

    async def GetPlaceByIata(  # type: ignore[override]  # noqa: N802
        self,
        request: places_pb2.GetPlaceByIataRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceByIataResponse:
        place = await self._places.find_by_iata(iata=request.iata)
        if not place:
            await context.abort(
                code=StatusCode.NOT_FOUND,
            )
        return places_pb2.GetPlaceByIataResponse(place=place)

    async def ListPlaces(  # type: ignore[override]  # noqa: N802
        self,
        request: places_pb2.ListPlacesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListPlacesResponse:
        found_places = await self._places.find_with_filters(
            filters=request.filters,
            cursor=request.page_token,
        )
        found_places.limit(limit=request.page_size)
        return places_pb2.ListPlacesResponse(
            places=[place async for place in found_places],
            next_page_token=await found_places.cursor(),
        )
