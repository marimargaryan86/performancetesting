from __future__ import annotations

import contextlib
import datetime
import ipaddress

import pydantic
from grpc import aio
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers as provider_offers
from snowfall.project.junction.provider import service
from snowfall.project.junction.provider.v1alpha import meta_pb2, meta_pb2_grpc
from snowfall.project.junction.service.providers.mock import (
    bookings,
    cache,
    offers,
    pricing,
)
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc import service as grpc_service


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    redis_dsn: pydantic.AnyUrl
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


class _OffersSettings(service.OffersSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


class _PriceQuotesSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: pydantic.AnyUrl
    provider_company_id: str
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


class _BookingsSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: pydantic.AnyUrl


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

    async def GetIdentity(  # type: ignore[override] # noqa: N802
        self,
        request: meta_pb2.GetIdentityRequest,
        context: aio.ServicerContext,
    ) -> meta_pb2.GetIdentityResponse:
        return meta_pb2.GetIdentityResponse(id="f9ce75d1-2025-4ab5-b5d7-69e4c14c053e")


async def _grpc(app: service.AsyncApplication[_GrpcSettings]) -> None:
    redis_connection = await app.stack.enter_async_context(
        aioredis.from_url(
            app.settings.redis_dsn,
            decode_responses=False,
        ).client(),
    )
    redis_client = redis.Client(redis_connection, prefix=app.name)
    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            _MockService(),
            provider_offers.OfferSearchService(
                provider_offers.TripOfferSearcher.from_implementation(
                    implementation=provider_offers.OfferSearchImplementation(
                        search_criteria_task_generator=offers.criteria_task_generator,
                        search_criteria_generator=offers.criteria_generator,
                        offer_group_cache_key_generator=offers.cache_key,
                        offer_group_generator=offers.offer_group_generator(
                            generator=offers.Generator(
                                option_cache=cache.OptionCache(client=redis_client),
                                ttl=app.settings.ttl,
                            ),
                        ),
                    ),
                    redis_client=redis_client,
                ),
            ),
        ],
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
        offer_group_generator=offers.offer_group_generator(
            generator=offers.Generator(
                option_cache=cache.OptionCache(
                    client=redis.Client(redis_conn, prefix=app.name),
                ),
                ttl=app.settings.ttl,
            ),
        ),
    )


async def _price_quotes(app: service.AsyncApplication[_PriceQuotesSettings]) -> None:
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            app.settings.redis_dsn,
            decode_responses=False,
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )

    await pricing.Consumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_prices".format(app.name),
            binds=[(types.Exchange("prices"), "offers.pricing")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("prices"),
        ),
        quoter=pricing.Quoter(
            option_cache=cache.OptionCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            price_quote_cache=cache.PriceQuoteCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            ttl=app.settings.ttl,
        ),
        provider_company_id=app.settings.provider_company_id,
    ).consume()


async def _bookings(app: service.AsyncApplication[_BookingsSettings]) -> None:
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            app.settings.redis_dsn,
            decode_responses=False,
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        types.Connection(app.settings.amqp_dsn),
    )

    await bookings.Consumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.offers")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("orders"),
        ),
        booker=bookings.Booker(
            price_quote_cache=cache.PriceQuoteCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
        ),
    ).consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="mock")

    entrypoint.enable_offers(_OffersSettings, _offers_search)
    entrypoint.enter_with_commands(
        service.Command(
            name="pricing",
            callback=_price_quotes,
            settings_class=_PriceQuotesSettings,
        ),
        service.Command(
            name="orders",
            callback=_bookings,
            settings_class=_BookingsSettings,
        ),
        service.Command(name="grpc", callback=_grpc, settings_class=_GrpcSettings),
    )
