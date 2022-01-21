import uuid

from grpc import StatusCode, aio

from snowfall.junction.places.places import PlaceRepository
from snowfall.junction.places.v1alpha import places_pb2, places_pb2_grpc
from snowfall.persistence import cursor
from snowfall.persistence.mongo import NotFoundError
from snowfall.transport.grpc import Service


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
        try:
            uuid.UUID(request.id)
        except ValueError:
            await context.abort(StatusCode.INVALID_ARGUMENT)

        try:
            place = await self._places.get_by_id(request.id)
        except NotFoundError:
            await context.abort(StatusCode.NOT_FOUND)

        return places_pb2.GetPlaceResponse(
            place=place,
        )

    async def ListPlaces(  # type: ignore[override] # noqa: N802
        self,
        request: places_pb2.ListPlacesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListPlacesResponse:
        cur = None

        if request.page_token:
            try:
                cur = cursor.unmarshal(request.page_token)
            except cursor.CursorError:
                await context.abort(StatusCode.INVALID_ARGUMENT)

        places_result = await self._places.find(cur=cur)
        limit = request.page_size

        if not limit:
            limit = self._default_page_size

        places = [place async for place in places_result.records(limit=limit)]
        cur = await places_result.cursor()
        page_token = None

        if cur:
            page_token = cursor.marshal(cur)

        return places_pb2.ListPlacesResponse(
            places=places,
            next_page_token=page_token or "",
        )
