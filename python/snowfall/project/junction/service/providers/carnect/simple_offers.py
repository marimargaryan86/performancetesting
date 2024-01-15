from __future__ import annotations

import contextlib

from aio_pika import abc
from redis import asyncio as aioredis

from snowfall.project.junction.provider import simple_offers
from snowfall.project.junction.service.providers.carnect import (
    adapter,
    cache,
    config,
    criteria,
)
from snowfall.project.junction.service.providers.carnect.v1 import amqp_pb2
from snowfall.stdlib.service import application

_Impl = simple_offers.SimpleOfferSearchImplementation[amqp_pb2.Criteria]


async def simple_search_app(
    app: application.Application[config.Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    carnect_adapter = adapter.CarnectOffersAdapter()

    return simple_offers.SimpleOfferSearchImplementation(
        search_criteria_task_generator=criteria.simple_search_criteria_task_generator,
        search_criteria_generator=criteria.simple_search_criteria_generator,
        offer_group_cache_key_generator=cache.generate_cache_key,
        offer_group_generator=carnect_adapter.gather_offer_groups,
    )
