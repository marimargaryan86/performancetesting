import contextlib
import random

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers, repository
from snowfall.project.junction.service.providers.duffel import cache
from snowfall.project.junction.service.providers.duffel.config import SearchesSettings
from snowfall.project.junction.service.providers.duffel.search import adapter
from snowfall.project.junction.service.providers.duffel.v1alpha import amqp_pb2
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, trackable, types
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders.offer_request import OfferRequestData

_OFFERS = "offers"


async def searches(app: service.Application[SearchesSettings]) -> None:  # noqa: WPS210
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                timeout=app.settings.http_timeout,
            ),
        )
        logging.register(http_client)
        metrics.register(http_client)
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        duffel_client = client.DuffelClient(
            api_base_url=app.settings.api_base_url,
            api_key=app.settings.api_key,
            version=app.settings.api_version,
            http_client=http_client,
        )
        duffle_adapter = adapter.DuffelSearchAdapter(
            duffel_client=duffel_client,
            offers_cache=cache.OfferCache(
                client=redis.Client[bytes](redis_connection, prefix=app.name),
            ),
            ttl=app.settings.ttl,
            enabled_airlines=app.settings.enabled_airlines,
            disabled_airlines=app.settings.disabled_airlines,
        )
        search_consumer = offers.SearchCriteriaConsumer[
            amqp_pb2.SearchCriteriaTask,
            OfferRequestData,
        ](
            provider_company_id=app.settings.provider_company_id,
            search_criteria_generator_func=duffle_adapter.search_criteria_generator,
            consumer=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_searches".format(app.name),
                binds=[(types.Exchange("duffel"), "offers.search.trip")],
                middleware_stack=[
                    trackable.ReportingMiddleware(
                        status_reporter=trackable.StatusReporter(
                            producer=producer.Producer(
                                connection=amqp_connection,
                                exchange=types.Exchange("duffel"),
                            ),
                        ),
                    ).execute,
                ],
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
                offer_group_cache_key_func=duffle_adapter.generate_cache_key,
                offer_group_generator=duffle_adapter.gather_search_results,
            ),
        )

        await search_consumer.consume()
