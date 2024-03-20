from __future__ import annotations

import contextlib
import datetime

import pydantic
from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import meta, searches, service
from snowfall.project.junction.rocket.service.providers.mock import (
    cache,
    pricing,
)
from snowfall.project.junction.rocket.service.providers.mock import (
    searches as provider_searches,
)
from snowfall.project.junction.rocket.service.providers.mock.constant import PROVIDER_ID
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import amqp_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types

_PROVIDER_NAME = "Mock"
_PROVIDERS_TO_DISABLED_OPERATORS = dict[str, list[str]]
_RESELLERS_TO_PROVIDER_OPERATORS = dict[str, _PROVIDERS_TO_DISABLED_OPERATORS]


class _Settings(service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    storage_dsn: service.AnyDsn
    reseller_disabled_operators: _RESELLERS_TO_PROVIDER_OPERATORS = pydantic.Field(
        default_factory=dict,
    )


class _PricingSettings(service.ProviderSettings):
    amqp_dsn: pydantic.AmqpDsn


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=PROVIDER_ID, name=_PROVIDER_NAME)


async def _search_factory(
    app: service.Application[_Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> searches.SearchImplementation[provider_searches.Criteria]:
    search_result_generator = provider_searches.search_result_generator(
        generator=provider_searches.Generator(
            search_result_cache=cache.SearchResultCache(
                client=redis.Client(redis_conn, prefix=app.name),
            ),
            ttl=app.settings.ttl,
        ),
    )

    return searches.SearchImplementation(
        search_criteria_task_generator=provider_searches.search_criteria_task_generator,
        search_result_cache_key_generator=provider_searches.cache_key,
        search_result_generator=search_result_generator,
    )


async def _pricing(app: service.Application[_PricingSettings]) -> None:
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    quote_task_consumer = pricing.QuoteTaskConsumer(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_pricing_consumer".format(app.name),
            binds=[(types.Exchange("searches"), "searches.pricing")],
        ),
        quote_result_producer=pricing.QuoteResultProducer(
            producer_obj=producer.Producer(connection, types.Exchange("searches")),
            routing_key="searches.pricing_results",
        ),
    )

    await quote_task_consumer.consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="mock",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        search_factory=_search_factory,
    )

    entrypoint.add_command(
        service.Command(
            name="pricing",
            callback=_pricing,
            settings_class=_PricingSettings,
        ),
    )

    entrypoint.enter()
