from __future__ import annotations

import logging as core_logging
import pathlib

import httpx
from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.provider import meta, offers, service
from snowfall.project.junction.provider.v1 import meta_pb2
from snowfall.project.junction.service.providers.direct_ferries import (
    adapter,
    booking,
    cache,
    config,
    criteria,
    orchestrator,
    port,
    route,
)
from snowfall.project.junction.service.providers.direct_ferries import (
    consumer as df_consumer,
)
from snowfall.project.junction.service.providers.direct_ferries.constant import (
    PROVIDER_ID,
)
from snowfall.project.junction.service.providers.direct_ferries.gtfs import (
    converter,
    gtfs_generator,
)
from snowfall.project.junction.service.providers.direct_ferries.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory, httpx_factory, redis_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base
from snowfall.vendor.direct_ferries.models import request

_OFFERS = "offers"
_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    request.QuoteRequest,
]

_PROVIDER_NAME = "Direct Ferries"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=PROVIDER_ID,
        name=_PROVIDER_NAME,
        trip_search_capabilities=meta_pb2.TripSearchCapabilities(
            supports_simple_search=False,
            supports_trip_search=True,
        ),
    )


def _create_client(
    http_client: httpx.AsyncClient,
    setting: config.DfBaseSettings,
) -> client.DfHttpClient:
    return client.DfHttpClient(
        auth_client=auth.AuthClient(
            api_url=str(setting.affiliate_api_url),
            client_secret=setting.client_secret,
            client_id=setting.client_id,
            http_client=http_client,
        ),
        http_client=http_client,
        config=base.ClientConfig(
            api_url=str(setting.api_url).rstrip("/"),
            partner_code=setting.partner_code,
            client_id=setting.client_id,
            client_secret=setting.client_secret,
            timeout=int(setting.api_timeout.total_seconds()),
        ),
    )


async def _offers(
    app: service.Application[config.Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
) -> _Impl:
    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)
    ferry_adapter = adapter.DfAdapter(
        df_client=_create_client(
            http_client=http_client,
            setting=app.settings,
        ),
        ports=port.PortRepository(port.load_ports()),
        offers_cache=cache.OffersCache(
            client=redis.Client[bytes](
                redis_conn,
                prefix=app.name,
            ),
        ),
        ttl=app.settings.ttl,
    )

    return offers.OfferSearchImplementation(
        search_criteria_task_generator=criteria.CriteriaGenerator(
            h3_port_mapping=h3.H3MappingRepository[port.Port](
                mapping=port.load_ports(),
                resolution=8,
            ),
            routes=route.RouteRepository(),
        ).from_search_task,
        search_criteria_generator=ferry_adapter.search_criteria_generator,
        offer_group_cache_key_generator=ferry_adapter.generate_cache_key,
        offer_group_generator=ferry_adapter.gather_search_results,
        allowed_window_td=app.settings.allowed_window_td,
    )


async def _orders(app: service.Application[config.OrdersSettings]) -> None:
    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)
    amqp_conn = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )

    offers_cache = cache.OffersCache(
        client=redis_client,
    )

    orders_consumer = df_consumer.OrdersConsumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_conn,
            queue_name="{0}_orders".format(app.name),
            binds=[(types.Exchange("orders"), "orders.offers")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_conn,
            exchange=types.Exchange("orders"),
        ),
        bookings=booking.BookingHandler(
            df_client=_create_client(
                http_client=http_client,
                setting=app.settings,
            ),
        ),
        offers_cache=offers_cache,
    )

    await orders_consumer.consume()


async def _price_quotes(
    app: service.Application[config.PriceQuotesSettings],
) -> None:
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    await df_consumer.PriceQuoteConsumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_prices".format(app.name),
            binds=[(types.Exchange("prices"), "offers.pricing")],
        ),
        producer_obj=producer.Producer(
            connection=amqp_connection,
            exchange=types.Exchange("prices"),
        ),
        offer_cache=cache.OffersCache(
            client=redis_client,
        ),
        price_ttl=app.settings.ttl,
        provider_company_id=app.settings.provider_company_id,
        routes=route.RouteRepository(),
    ).consume()


async def _create_gtfs(app: service.Application[config.GtfsSetting]) -> None:
    httpx_logger = core_logging.getLogger("httpx")
    httpx_logger.setLevel(core_logging.WARNING)

    output_path = pathlib.Path(app.settings.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)
    df_client = _create_client(
        http_client=http_client,
        setting=app.settings,
    )

    timetable_responses = await orchestrator.timetables_from_routes(
        df_client=df_client,
        routes=[
            route_obj
            async for route_obj in orchestrator.routes_for_operators(
                df_client=df_client,
                operators=(
                    await df_client.operators.get_operators()
                ).operator_data.operators,
            )
        ],
    )

    converter_obj = converter.DFDataConverter(
        timetable_responses=timetable_responses,
    )

    await gtfs_generator.GTFSGenerator(app.settings.output_path).generate_feed(
        converter=converter_obj,
    )


async def _static(app: service.Application[config.StaticSettings]) -> None:
    http_client = await httpx_factory.make_client(app, timeout=app.settings.api_timeout)
    df_client = _create_client(http_client, app.settings)

    if not app.settings.dump_routes and not app.settings.dump_ports:
        return

    routes = [
        route_obj
        async for route_obj in orchestrator.routes_for_operators(
            df_client=df_client,
            operators=(
                await df_client.operators.get_operators()
            ).operator_data.operators,
        )
    ]

    if app.settings.dump_ports:
        output_path = str(app.settings.ports_path) if app.settings.ports_path else None

        await port.make_ports_from_routes(routes, output_path)

    if app.settings.dump_routes:
        passenger_info_per_route = {
            route_info.route_id: route_info
            for route_info in await orchestrator.passenger_info_for_routes(
                df_client=df_client,
                routes=routes,
            )
        }
        output_path = str(app.settings.ports_path) if app.settings.ports_path else None
        await route.make_routes(routes, passenger_info_per_route, output_path)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="junction-providers-direct-ferries",
        settings_class=config.Settings,
        meta_factory=_meta_factory,
        offers_factory=_offers,
    )

    entrypoint.enter_with_commands(
        service.Command(
            name="orders",
            callback=_orders,
            settings_class=config.OrdersSettings,
        ),
        service.Command(
            name="pricing",
            callback=_price_quotes,
            settings_class=config.PriceQuotesSettings,
        ),
        service.Command(
            name="export",
            callback=_create_gtfs,
            settings_class=config.GtfsSetting,
        ),
        service.Command(
            name="statics",
            callback=_static,
            settings_class=config.StaticSettings,
        ),
    )
