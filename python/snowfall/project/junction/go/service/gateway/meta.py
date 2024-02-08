import asyncio

from grpc import aio

from snowfall.project.junction.go.service.gateway import providers
from snowfall.project.junction.go.service.gateway.v1 import (
    meta_pb2,
    meta_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class Service(service.Service, meta_pb2_grpc.MetaServiceServicer):
    def __init__(self, providers_collection: providers.Collection):
        self._providers = providers_collection

    def get_name(self) -> str:
        return meta_pb2.DESCRIPTOR.services_by_name["MetaService"].full_name

    def register(self, server: aio.Server) -> None:
        meta_pb2_grpc.add_MetaServiceServicer_to_server(self, server)

    async def ListProviders(  # type: ignore[override] # noqa: N802
        self,
        request: meta_pb2.ListProvidersRequest,
        context: aio.ServicerContext,
    ) -> meta_pb2.ListProvidersResponse:
        return meta_pb2.ListProvidersResponse(
            providers=[
                meta_pb2.Provider(
                    id=provider.identifier,
                    name=provider.name,
                    is_healthy=self._providers.is_healthy(provider.identifier),
                )
                async for provider in self._providers.all_()
            ],
        )

    async def Sleep(  # type: ignore[override] # noqa: N802
        self,
        request: meta_pb2.SleepRequest,
        context: aio.ServicerContext,
    ) -> meta_pb2.SleepResponse:
        await asyncio.sleep(request.duration_seconds)

        return meta_pb2.SleepResponse(
            text="Have a great day and thanks for the hard work!",
        )
