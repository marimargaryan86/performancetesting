import contextlib
import random

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers
from snowfall.project.junction.service.providers.ba_ndc import cache
from snowfall.project.junction.service.providers.ba_ndc.config import SearchesSettings
from snowfall.project.junction.service.providers.ba_ndc.search import adapter
from snowfall.project.junction.service.providers.ba_ndc.v1alpha import amqp_pb2
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation import httpx_metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, trackable, types
from snowfall.vendor.ba_ndc import client


async def searches(app: service.Application[SearchesSettings]) -> None:  # noqa: WPS210
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx_metrics.with_metrics(
                httpx.AsyncClient(
                    http2=True,
                    timeout=app.settings.http_timeout,
                ),
            ),
        )
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        ba_ndc_client = client.BaNdcClient(
            api_base_url=app.settings.api_base_url,
            api_key=app.settings.api_key,
            http_client=http_client,
        )

        search_consumer = offers.SearchCriteriaConsumer[amqp_pb2.SearchCriteriaTask](
            consumer=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_searches".format(app.name),
                binds=[(types.Exchange("ba_ndc"), "offers.search.trip")],
                middleware_stack=[
                    trackable.ReportingMiddleware(
                        status_reporter=trackable.StatusReporter(
                            producer=producer.Producer(
                                connection=amqp_connection,
                                exchange=types.Exchange("ba_ndc"),
                            ),
                        ),
                    ).execute,
                ],
            ),
            producer=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange("offers"),
            ),
            redis=redis.Client(
                redis=redis_connection,
                prefix=app.name,
            ),
            offer_group_cache_key_func=adapter.offer_group_cache_key,
            offer_group_generator=adapter.BaNdcSearchAdapter(
                ba_ndc_client=ba_ndc_client,
                offers_cache=cache.OfferCache(
                    client=redis.Client[bytes](redis_connection, prefix=app.name),
                ),
            ).gather_search_results,
        )

        await search_consumer.consume()
