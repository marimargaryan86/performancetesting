from __future__ import annotations

import contextlib
import ipaddress

from grpc import aio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers as provider_offers
from snowfall.project.junction.provider import service
from snowfall.project.junction.provider.v1alpha import meta_pb2, meta_pb2_grpc
from snowfall.project.junction.service.providers.mock import offers, orders
from snowfall.stdlib.transport.amqp import types
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc import service as grpc_service


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051


class _OffersSettings(service.OffersSettings):
    """The bare minimum of configuration."""


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


async def _offers_search(
    app: service.Application[_OffersSettings],
    amqp_conn: types.Connection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> provider_offers.OfferSearchImplementation[offers.Criteria, offers.Criteria]:
    return provider_offers.OfferSearchImplementation(
        search_criteria_task_generator=offers.criteria_task_generator,
        search_criteria_generator=offers.criteria_generator,
        offer_group_cache_key_generator=offers.cache_key,
        offer_group_generator=offers.offer_group_generator,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="mock")

    entrypoint.enable_offers(_OffersSettings, _offers_search)
    entrypoint.enter_with_commands(
        service.Command(
            name="orders",
            callback=orders.orders,
            settings_class=orders.OrdersSettings,
        ),
        service.Command(name="grpc", callback=_grpc, settings_class=_GrpcSettings),
    )
