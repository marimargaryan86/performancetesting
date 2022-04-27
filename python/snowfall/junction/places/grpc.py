import uuid

from grpc import StatusCode, aio

from snowfall.junction.places.places import CuratedPlaceRepository, PlaceRepository
from snowfall.junction.places.v1alpha import places_pb2, places_pb2_grpc
from snowfall.stdlib.transport.grpc import Service


class PlacesService(Service, places_pb2_grpc.PlacesServiceServicer):
    def __init__(self, places: PlaceRepository, default_page_size: int):
        self._default_page_size = default_page_size
        self._places = places

    def get_name(self) -> str:
        return places_pb2.DESCRIPTOR.services_by_name["PlacesService"].full_name

    def register(self, server: aio.Server) -> None:
        places_pb2_grpc.add_PlacesServiceServicer_to_server(self, server)

    async def GetPlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.GetPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceResponse:
        place = await self._places.find_by_id(request.id)

        if not place:
            await context.abort(StatusCode.NOT_FOUND)

        return places_pb2.GetPlaceResponse(place=place)

    async def ListPlaces(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.ListPlacesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListPlacesResponse:
        places_result = await self._places.find(request.page_token)

        places_result.limit(
            request.page_size
            if request.page_size is not None
            else self._default_page_size,
        )

        return places_pb2.ListPlacesResponse(
            places=[place async for place in places_result],
            next_page_token=await places_result.cursor(),
        )


class CuratedPlacesService(  # noqa: WPS214
    Service,
    places_pb2_grpc.CuratedPlacesServiceServicer,
):
    def __init__(self, places: CuratedPlaceRepository, default_page_size: int):
        self._default_page_size = default_page_size
        self._places = places

    def get_name(self) -> str:
        return places_pb2.DESCRIPTOR.services_by_name["CuratedPlacesService"].full_name

    def register(self, server: aio.Server) -> None:
        places_pb2_grpc.add_CuratedPlacesServiceServicer_to_server(self, server)

    async def GetCuratedPlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.GetPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetCuratedPlaceResponse:
        try:
            uuid.UUID(request.id)
        except ValueError:
            await context.abort(StatusCode.INVALID_ARGUMENT)

        place_result = await self._places.find_by_id(request.id)

        return places_pb2.GetCuratedPlaceResponse(place=place_result)

    async def ListCuratedPlaces(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.ListCuratedPlacesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListCuratedPlacesResponse:
        places_result = await self._places.find(request.page_token)

        places_result.limit(
            request.page_size
            if request.page_size is not None
            else self._default_page_size,
        )

        return places_pb2.ListCuratedPlacesResponse(
            places=[place async for place in places_result],
            next_page_token=await places_result.cursor(),
        )

    async def CreateCuratedPlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.CreateCuratedPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.CreateCuratedPlaceResponse:
        await self._places.create(request.place)

        return places_pb2.CreateCuratedPlaceResponse()

    async def DeleteCuratedPlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.DeleteCuratedPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.DeleteCuratedPlaceResponse:
        try:
            uuid.UUID(request.id)
        except ValueError:
            await context.abort(StatusCode.INVALID_ARGUMENT)

        await self._places.delete(request.id)

        return places_pb2.DeleteCuratedPlaceResponse()

    async def UpdateCuratedPlace(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.UpdateCuratedPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.UpdateCuratedPlaceResponse:
        try:
            uuid.UUID(request.id)
        except ValueError:
            await context.abort(StatusCode.INVALID_ARGUMENT)

        await self._places.update(request.id, request.place)

        return places_pb2.UpdateCuratedPlaceResponse()
