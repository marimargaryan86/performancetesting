import datetime
from collections.abc import Awaitable, Callable, Mapping

from snowfall.project.junction.go.service.places.v1 import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)

ResolvedMap = Mapping[str, models_pb2.Place]


ResolverFunc = Callable[[frozenset[str]], Awaitable[ResolvedMap]]


class Resolver(object):
    def __init__(
        self,
        stub: places_pb2_grpc.PlacesServiceStub,
        timeout: datetime.timedelta,
    ):
        self._stub = stub
        self._timeout = timeout

    async def from_ids(self, ids: frozenset[str]) -> ResolvedMap:
        response: places_pb2.ListPlacesResponse = await self._stub.ListPlaces(
            request=places_pb2.ListPlacesRequest(
                page_size=len(ids),
                ids=models_pb2.ListOfIds(ids=list(ids)),
            ),
            timeout=self._timeout.total_seconds(),
        )

        return {place.location.id: place for place in response.places}
