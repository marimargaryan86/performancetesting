import contextlib
import random

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers, repository
from snowfall.project.junction.service.providers.distribusion import cache
from snowfall.project.junction.service.providers.distribusion.config import (
    SearchesSettings,
)
from snowfall.project.junction.service.providers.distribusion.search import adapter
from snowfall.project.junction.service.providers.distribusion.v1alpha import amqp_pb2
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, trackable, types
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.models.criterias import FindConnectionsCriteria


async def searches(app: service.Application[SearchesSettings]) -> None:  # noqa: WPS210
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
            ),
        )
        logging.register(http_client)
        metrics.register(http_client)
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
        distribusion_adapter = adapter.DistribusionSearchAdapter(
            distribusion_client=distribusion_client,
            offers_cache=cache.OffersCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            ttl=app.settings.ttl,
        )
        search_consumer = offers.SearchCriteriaConsumer[
            amqp_pb2.SearchCriteriaTask,
            FindConnectionsCriteria,
        ](
            provider_company_id=app.settings.provider_company_id,
            search_criteria_generator_func=distribusion_adapter.search_criteria_generator,
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
            offer_group_repository=repository.OfferGroupRepository(
                redis=redis.Client(
                    redis=redis_connection,
                    prefix=app.name,
                ),
                offer_group_cache_key_func=distribusion_adapter.generate_cache_key,
                offer_group_generator=distribusion_adapter.gather_search_results,
            ),
        )

        await search_consumer.consume()
