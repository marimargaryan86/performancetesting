import contextlib
import datetime
import random
from typing import Sequence

import httpx
import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers
from snowfall.project.junction.service.providers.distribusion import cache, config
from snowfall.project.junction.service.providers.distribusion.search import (
    adapter,
    validator,
)
from snowfall.project.junction.service.providers.distribusion.v1alpha import amqp_pb2
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, trackable, types
from snowfall.vendor.distribusion import client

_DEFAULT_TTL_IN_MINUTES = 45


class SearchesSettings(config.DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)


async def searches(app: service.Application[SearchesSettings]) -> None:  # noqa: WPS210
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
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
        distribusion_client = client.DistribusionClient(
            api_base_url=app.settings.api_base_url,
            api_key=app.settings.api_key,
            retailer_partner_number=app.settings.retailer_partner_number,
            http_client=http_client,
        )
        search_consumer = offers.SearchCriteriaConsumer[amqp_pb2.SearchCriteriaTask](
            consumer=consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_searches".format(app.name),
                binds=[(types.Exchange("distribusion"), "offers.search.trip")],
                middleware_stack=[
                    trackable.ReportingMiddleware(
                        status_reporter=trackable.StatusReporter(
                            producer=producer.Producer(
                                connection=amqp_connection,
                                exchange=types.Exchange("distribusion"),
                            ),
                        ),
                    ).execute,
                ],
            ),
            producer=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange("offers"),
            ),
            redis=redis.Client[bytes](
                redis=redis_connection,
                prefix=app.name,
            ),
            offer_group_cache_key_func=adapter.offer_group_cache_key,
            offer_group_generator=adapter.DistribusionSearchAdapter(
                distribusion_client=distribusion_client,
                connection_validator=validator.ConnectionValidator(),
                offers_cache=cache.OffersCache(
                    client=redis.Client(redis_connection, prefix=app.name),
                ),
                ttl=app.settings.ttl,
            ).gather_search_results,
        )

        await search_consumer.consume()
