from __future__ import annotations

import contextlib

import httpx
from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.rocket.provider import meta, searches, service
from snowfall.project.junction.rocket.provider.v1alpha import meta_pb2
from snowfall.project.junction.rocket.service.providers.direct_ferries import (
    cache,
    config,
    constant,
)
from snowfall.project.junction.rocket.service.providers.direct_ferries import (
    searches as provider_searches,
)
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import httpx_factory
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base

_PROVIDER_NAME = "Direct Ferries"
_API_TIMEOUT_DEFAULT_SECONDS = 40


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(
        identifier=constant.PROVIDER_ID,
        name=_PROVIDER_NAME,
        search_capabilities=meta_pb2.SearchCapabilities(ferry=True),
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
        ),
    )


async def _search_factory(
    app: service.Application[config.Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> searches.SearchImplementation[provider_searches.Criteria]:
    httpx_client = await httpx_factory.make_client(
        app,
        timeout=app.settings.api_timeout,
    )

    search_result_generator = provider_searches.SearchResultGenerator(
        df_client=_create_client(
            httpx_client,
            setting=app.settings,
        ),
        offers_cache=cache.OffersCache(
            client=redis.Client[bytes](
                redis_conn,
                prefix=app.name,
            ),
        ),
        ttl=app.settings.ttl,
    )

    return searches.SearchImplementation(
        search_criteria_task_generator=provider_searches.CriteriaGenerator().criteria_task_generator,
        search_result_cache_key_generator=provider_searches.cache_key,
        search_result_generator=search_result_generator.generate,
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(
        name="direct-ferries",
        settings_class=config.Settings,
        meta_factory=_meta_factory,
        search_factory=_search_factory,
    )

    entrypoint.enter()
