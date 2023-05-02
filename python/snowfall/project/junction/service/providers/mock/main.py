import ipaddress

from grpc import aio

from snowfall.project.junction.provider.v1alpha import meta_pb2, meta_pb2_grpc
from snowfall.project.junction.service.providers.mock import offers, orders
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc import service as grpc_service


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class _MockService(grpc_service.Service, meta_pb2_grpc.MetaServiceServicer):
    def get_name(self) -> str:
        return meta_pb2.DESCRIPTOR.services_by_name["MetaService"].full_name

    def register(self, server: aio.Server) -> None:
        meta_pb2_grpc.add_MetaServiceServicer_to_server(self, server)

    async def GetCapabilities(  # type: ignore[override] # noqa: N802
        self,
        request: meta_pb2.GetCapabilitiesRequest,
        context: aio.ServicerContext,
    ) -> meta_pb2.GetCapabilitiesResponse:
        return meta_pb2.GetCapabilitiesResponse()

    async def GetIdentifier(  # type: ignore[override] # noqa: N802
        self,
        request: meta_pb2.GetIdentifierRequest,
        context: aio.ServicerContext,
    ) -> meta_pb2.GetIdentifierResponse:
        return meta_pb2.GetIdentifierResponse(identifier="foo")


async def _grpc(app: service.Application[_GrpcSettings]) -> None:
    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [_MockService()],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="mock")

    entrypoint.enter_with_commands(
        service.Command(
            name="offers",
            callback=offers.offers,
            settings_class=offers.OffersSettings,
        ),
        service.Command(
            name="orders",
            callback=orders.orders,
            settings_class=orders.OrdersSettings,
        ),
        service.Command(name="grpc", callback=_grpc, settings_class=_GrpcSettings),
    )
