from __future__ import annotations

import contextlib
import datetime

from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import meta, searches, service
from snowfall.project.junction.rocket.service.providers.mock import (
    cache,
)
from snowfall.project.junction.rocket.service.providers.mock import (
    searches as provider_searches,
)
from snowfall.project.junction.rocket.service.providers.mock.constant import PROVIDER_ID
from snowfall.stdlib.persistence.redis import types as redis

_PROVIDER_NAME = "Mock"


class _Settings(service.ProviderSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    storage_dsn: service.AnyDsn
    # TODO(reuben.t): add disabled operator logic, once operator is available in  model


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


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="mock",
        settings_class=_Settings,
        meta_factory=_meta_factory,
        search_factory=_search_factory,
    )

    entrypoint.enter()
