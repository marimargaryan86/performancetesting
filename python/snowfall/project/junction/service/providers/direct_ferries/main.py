from __future__ import annotations

import contextlib
import pathlib
import random

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers_v2 as offers
from snowfall.project.junction.provider import service
from snowfall.project.junction.service.providers.direct_ferries import (
    adapter,
    booking,
    cache,
    config,
)
from snowfall.project.junction.service.providers.direct_ferries import (
    consumer as df_consumer,
)
from snowfall.project.junction.service.providers.direct_ferries import (
    criteria,
    orchestrator,
    port,
    route,
)
from snowfall.project.junction.service.providers.direct_ferries.gtfs import (
    converter,
    gtfs_generator,
)
from snowfall.project.junction.service.providers.direct_ferries.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base
from snowfall.vendor.direct_ferries.models import request

_OFFERS = "offers"
_Impl = offers.OfferSearchImplementation[
    amqp_pb2.SearchCriteriaTask,
    request.QuoteRequest,
]


def _create_client(
    http_client: httpx.AsyncClient,
    setting: config.DfBaseSettings,
) -> client.DfHttpClient:
    return client.DfHttpClient(
        auth_client=auth.AuthClient(
            api_url=setting.affiliate_api_url,
            client_secret=setting.client_secret,
            client_id=setting.client_id,
            http_client=http_client,
        ),
        http_client=http_client,
        config=base.ClientConfig(
            api_url=setting.api_url,
            partner_code=setting.partner_code,
            client_id=setting.client_id,
            client_secret=setting.client_secret,
            timeout=int(setting.api_timeout.total_seconds()),
        ),
    )


async def _offers(
    app: service.Application[config.OffersSettings],
    amqp_conn: types.Connection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            timeout=int(app.settings.api_timeout.total_seconds()),
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
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
    )


async def _orders(app: service.Application[config.OrdersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
        )
        logging.register(http_client)
        metrics.register(http_client)
        amqp_conn = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),  # nosec
        )
        redis_conn = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=True,
            ).client(),
        )

        offers_cache = cache.OffersCache(
            client=redis.Client(redis_conn, prefix=app.name),
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


async def _price_quotes(app: service.Application[config.PriceQuotesSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                app.settings.redis_dsn,
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )

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
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            price_ttl=app.settings.ttl,
            provider_company_id=app.settings.provider_company_id,
        ).consume()


async def _create_gtfs(app: service.Application[config.GtfsSetting]) -> None:
    output_path = pathlib.Path(app.settings.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
        )
        logging.register(http_client)
        metrics.register(http_client)
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
                    ).operator_data.operators[:15],
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
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
        )
        logging.register(http_client)
        metrics.register(http_client)
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
            output_path = (
                str(app.settings.ports_path) if app.settings.ports_path else None
            )

            await port.make_ports_from_routes(routes, output_path)

        if app.settings.dump_routes:
            output_path = (
                str(app.settings.ports_path) if app.settings.ports_path else None
            )
            await route.make_routes(routes, output_path)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="direct_ferries")

    entrypoint.enable_offers(config.OffersSettings, _offers)
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
