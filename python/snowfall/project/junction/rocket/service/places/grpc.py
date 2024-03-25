from grpc import aio

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

    def GetPlace(  # noqa: N802
        self,
        request: places_pb2.GetPlaceRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceResponse:
        raise NotImplementedError

    def GetPlaceClosestToCoordinates(  # noqa: N802
        self,
        request: places_pb2.GetPlaceClosestToCoordinatesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceClosestToCoordinatesResponse:
        raise NotImplementedError

    def GetPlaceByIata(  # noqa: N802
        self,
        request: places_pb2.GetPlaceByIataRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.GetPlaceByIataResponse:
        raise NotImplementedError

    def ListPlaces(  # noqa: N802
        self,
        request: places_pb2.ListPlacesRequest,
        context: aio.ServicerContext,
    ) -> places_pb2.ListPlacesResponse:
        raise NotImplementedError
