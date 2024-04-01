from __future__ import annotations

import contextlib
import datetime

import pydantic
from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import meta, searches, service
from snowfall.project.junction.rocket.service.providers.carnect import (
    cache,
    criteria,
    pricing,
)
from snowfall.project.junction.rocket.service.providers.carnect import (
    searches as search_result_generator,
)
from snowfall.project.junction.rocket.service.providers.carnect.constants import (
    PROVIDER_ID,
)
from snowfall.stdlib.service import amqp_factory, httpx_factory
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.carnect import client
from snowfall.vendor.carnect import config as carnect_settings

_PROVIDER_NAME = "Carnect"

_DEFAULT_TTL_IN_MINUTES = 45
_DEFAULT_API_TIMEOUT_IN_SECONDS = 30


class _Settings(service.ProviderSettings):
    api_base_url: pydantic.AnyUrl
    api_username: str
    api_password: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_DEFAULT_API_TIMEOUT_IN_SECONDS,
    )
    env_name: str = "local"

    @property
    def is_test(self) -> bool:
        return self.env_name.lower() != "production"

    ttl: datetime.timedelta = datetime.timedelta(minutes=_DEFAULT_TTL_IN_MINUTES)
    storage_dsn: service.AnyDsn
    # TODO(reuben.t): add disabled operator logic, once operator is available in  model


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=PROVIDER_ID, name=_PROVIDER_NAME)


async def _search_factory(
    app: service.Application[_Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> searches.SearchImplementation[criteria.Criteria]:
    carnect_config = carnect_settings.Config(
        timeout=app.settings.ttl.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=True,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    carnect_client = client.CarnectClient(
        http_client=await httpx_factory.make_client(
            app,
            timeout=app.settings.api_timeout,
        ),
        config=carnect_config,
    )

    result_generator = search_result_generator.SearchResultGenerator(
        carnect_client=carnect_client,
        carnect_config=carnect_config,
        ttl=app.settings.ttl,
    )

    return searches.SearchImplementation(
        search_criteria_task_generator=criteria.search_criteria_generator,
        search_result_cache_key_generator=cache.generate_cache_key,
        search_result_generator=result_generator.gather_search_results,
    )


async def _pricing(
    app: service.Application[_Settings],
) -> None:
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    quote_task_consumer = pricing.QuoteTaskConsumer(
        consumer_obj=consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_pricing_consumer".format(app.name),
            binds=[(types.Exchange("searches"), "searches.pricing")],
        ),
        quote_result_producer=pricing.QuoteResultProducer(
            producer_obj=producer.Producer(amqp_connection, types.Exchange("searches")),
            routing_key="searches.pricing_results",
        ),
        ttl=app.settings.ttl,
    )

    await quote_task_consumer.consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="carnect",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        search_factory=_search_factory,
    )
    entrypoint.enter_with_commands(
        service.Command(
            name="pricing",
            callback=_pricing,
            settings_class=_Settings,
        ),
    )
