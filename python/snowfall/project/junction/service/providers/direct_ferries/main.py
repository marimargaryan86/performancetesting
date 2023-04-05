import contextlib
import datetime
import os
import pathlib
import random
from typing import Sequence

import httpx
import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers, repository
from snowfall.project.junction.provider.service import OffersSettings
from snowfall.project.junction.service.providers.direct_ferries import (
    adapter,
    booking,
    cache,
)
from snowfall.project.junction.service.providers.direct_ferries import (
    consumer as df_consumer,
)
from snowfall.project.junction.service.providers.direct_ferries import (
    criteria,
    port,
    route,
)
from snowfall.project.junction.service.providers.direct_ferries.gtfs import (
    converter,
    gtfs_generator,
    timetables,
)
from snowfall.project.junction.service.providers.direct_ferries.v1alpha import amqp_pb2
from snowfall.stdlib import h3, service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base
from snowfall.vendor.direct_ferries.models import request

_OFFERS = "offers"
dir_path = os.path.dirname(os.path.realpath(__file__))


class _SearchSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    api_url: pydantic.AnyUrl
    affiliate_api_url: pydantic.AnyUrl
    partner_code: str
    client_id: str
    client_secret: str
    api_timeout: datetime.timedelta = datetime.timedelta(seconds=40)
    provider_company_id: str


class _OffersSettings(OffersSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


class _OrdersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    api_url: pydantic.AnyUrl
    affiliate_api_url: pydantic.AnyUrl
    partner_code: str
    client_id: str
    client_secret: str
    api_timeout: datetime.timedelta = datetime.timedelta(seconds=40)
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


class _GtfsSetting(service.Settings):
    api_url: pydantic.AnyUrl
    affiliate_api_url: pydantic.AnyUrl
    partner_code: str
    client_id: str
    client_secret: str
    api_timeout: datetime.timedelta = datetime.timedelta(minutes=2)
    output_path: str = "dist/import/gtfs-feed/direct-ferries"


async def _searches(app: service.Application[_SearchSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )

        df_auth_client = auth.AuthClient(
            api_url=app.settings.affiliate_api_url,
            client_secret=app.settings.client_secret,
            client_id=app.settings.client_id,
            http_client=http_client,
        )
        df_client = client.DfHttpClient(
            auth_client=df_auth_client,
            http_client=http_client,
            config=base.ClientConfig(
                api_url=app.settings.api_url,
                partner_code=app.settings.partner_code,
                client_id=app.settings.client_id,
                client_secret=app.settings.client_secret,
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
        )

        redis_client = redis.Client(redis_connection, prefix=app.name)
        ferry_adapter = adapter.DfAdapter(
            df_client=df_client,
            ports=port.PortRepository(port.load_ports()),
            offers_cache=cache.OffersCache(
                client=redis_client,
            ),
            ttl=app.settings.ttl,
        )
        await offers.SearchCriteriaConsumer[
            amqp_pb2.SearchCriteriaTask,
            request.QuoteRequest,
        ](
            provider_company_id=app.settings.provider_company_id,
            search_criteria_generator_func=ferry_adapter.search_criteria_generator,
            consumer=consumer.Consumer(
                connection=amqp_connection,
                binds=[(types.Exchange("direct_ferries"), "offers.search.trip")],
                queue_name="{0}_searches".format(app.name),
            ),
            producer=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange(_OFFERS),
            ),
            offer_group_repository=repository.OfferGroupRepository(
                redis=redis.Client(
                    redis=redis_connection,
                    prefix=app.name,
                ),
                offer_group_cache_key_func=ferry_adapter.generate_cache_key,
                offer_group_generator=ferry_adapter.gather_search_results,
            ),
        ).consume()


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        amqp_conn = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        redis_conn = await stack.enter_async_context(
            aioredis.from_url(
                app.settings.redis_dsn,
                decode_responses=True,
            ).client(),
        )

        trip_search_consumer = offers.create_trip_offer_search_consumer(
            amqp_connection=amqp_conn,
            redis_client=redis.Client[str](redis_conn, prefix=app.name),
            criteria_generator=criteria.CriteriaGenerator(
                h3_port_mapping=h3.H3MappingRepository[port.Port](
                    mapping=port.load_ports(),
                    resolution=8,
                ),
                routes=route.RouteRepository(),
            ).from_search_task,
            internal_exchange_name=app.name,
        )

        await trip_search_consumer.consume()


async def _orders(app: service.Application[_OrdersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
        )
        amqp_conn = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),  # nosec
        )
        redis_conn = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=True,
            ).client(),
        )

        df_client = client.DfHttpClient(
            auth_client=auth.AuthClient(
                api_url=app.settings.affiliate_api_url,
                client_secret=app.settings.client_secret,
                client_id=app.settings.client_id,
                http_client=http_client,
            ),
            http_client=http_client,
            config=base.ClientConfig(
                api_url=app.settings.api_url,
                partner_code=app.settings.partner_code,
                client_id=app.settings.client_id,
                client_secret=app.settings.client_secret,
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
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
                df_client=df_client,
            ),
            offers_cache=offers_cache,
        )

        await orders_consumer.consume()


async def _price_quotes(app: service.Application[_OffersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
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


async def _create_gtfs(app: service.Application[_GtfsSetting]) -> None:
    output_path = pathlib.Path(app.settings.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=int(app.settings.api_timeout.total_seconds()),
            ),
        )

        timetable_repository = timetables.TimetableRepository(
            df_client=client.DfHttpClient(
                auth_client=auth.AuthClient(
                    api_url=app.settings.affiliate_api_url,
                    client_secret=app.settings.client_secret,
                    client_id=app.settings.client_id,
                    http_client=http_client,
                ),
                http_client=http_client,
                config=base.ClientConfig(
                    api_url=app.settings.api_url,
                    partner_code=app.settings.partner_code,
                    client_id=app.settings.client_id,
                    client_secret=app.settings.client_secret,
                    timeout=int(app.settings.api_timeout.total_seconds()),
                ),
            ),
        )

        timetable_responses = await timetable_repository.get_timetables()

    converter_obj = converter.DFDataConverter(
        timetable_responses=timetable_responses,
    )

    await gtfs_generator.GTFSGenerator(app.settings.output_path).generate_feed(
        converter=converter_obj,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="direct_ferries")
    entrypoint.enter_with_commands(
        service.Command(
            name="searches",
            callback=_searches,
            settings_class=_SearchSettings,
        ),
        service.Command(
            name="offers",
            callback=_offers,
            settings_class=_OffersSettings,
        ),
        service.Command(
            name="orders",
            callback=_orders,
            settings_class=_OrdersSettings,
        ),
        service.Command(
            name="pricing",
            callback=_price_quotes,
            settings_class=_OffersSettings,
        ),
        service.Command(
            name="export",
            callback=_create_gtfs,
            settings_class=_GtfsSetting,
        ),
    )
