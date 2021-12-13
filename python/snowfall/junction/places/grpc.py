from grpc import StatusCode, aio

from snowfall.junction.common.v1alpha import models_pb2
from snowfall.junction.places.places import NotFoundError, PlaceRepository
from snowfall.junction.places.v1alpha import places_pb2, places_pb2_grpc
from snowfall.transport.grpc import Service


class PlacesService(Service, places_pb2_grpc.PlacesServiceServicer):
    def __init__(self, places: PlaceRepository):
        self._places = places

    def get_name(self) -> str:
        return places_pb2.DESCRIPTOR.services_by_name["PlacesService"].full_name

    def register(self, server: aio.Server) -> None:
        places_pb2_grpc.add_PlacesServiceServicer_to_server(self, server)

    async def GetPlace(  # noqa: N802
        self,
        request: places_pb2.GetPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceResponse:
        try:
            place = await self._places.get(request.id)
        except NotFoundError:
            await context.abort(StatusCode.NOT_FOUND)

        return places_pb2.GetPlaceResponse(
            place=models_pb2.Place(id=str(place.identifier)),
        )

    async def ListPlaces(  # noqa: N802
        self,
        request: places_pb2.ListPlacesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListPlacesResponse:
        return places_pb2.ListPlacesResponse(
            places=[
                models_pb2.Place(id=str(place.identifier))
                for place in await self._places.find()
            ],
        )
