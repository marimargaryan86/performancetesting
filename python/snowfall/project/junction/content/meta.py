import dataclasses
import uuid

from grpc import aio

from snowfall.project.junction.provider.v2alpha import meta_pb2, meta_pb2_grpc
from snowfall.stdlib.transport.grpc import service


@dataclasses.dataclass(frozen=True)
class MetaImplementation(object):
    identifier: uuid.UUID
    name: str
    trip_search_capabilities: meta_pb2.TripSearchCapabilities | None = None


class MetaService(service.Service, meta_pb2_grpc.MetaServiceServicer):
    def __init__(self, implementation: MetaImplementation):
        self._provider_id = str(implementation.identifier)
        self._provider_name = implementation.name
        self._trip_search_capabilities = implementation.trip_search_capabilities

    def get_name(self) -> str:
        return meta_pb2.DESCRIPTOR.services_by_name["MetaService"].full_name

    def register(self, server: aio.Server) -> None:
        meta_pb2_grpc.add_MetaServiceServicer_to_server(self, server)

    async def GetCapabilities(  # type: ignore[override] # noqa: N802
        self,
        request: meta_pb2.GetCapabilitiesRequest,
        context: aio.ServicerContext,
    ) -> meta_pb2.GetCapabilitiesResponse:
        return meta_pb2.GetCapabilitiesResponse(
            trip_search_capabilities=self._trip_search_capabilities,
        )

    async def GetIdentity(  # type: ignore[override] # noqa: N802
        self,
        request: meta_pb2.GetIdentityRequest,
        context: aio.ServicerContext,
    ) -> meta_pb2.GetIdentityResponse:
        return meta_pb2.GetIdentityResponse(
            id=self._provider_id,
            name=self._provider_name,
        )
