import contextlib
import random
from typing import Sequence

import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers as provider_offers
from snowfall.project.junction.service.providers.distribusion import criteria, stations
from snowfall.stdlib import h3, service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types

_OFFERS = "offers"


class OffersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]


async def offers(app: service.Application[OffersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_conn = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=True,
            ).client(),
        )
        connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )

        trip_search_consumer = provider_offers.create_trip_offer_search_consumer(
            amqp_connection=connection,
            redis_client=redis.Client(redis_conn, prefix=app.name),
            criteria_generator=criteria.CriteriaGenerator(
                h3_mapping=h3.H3MappingRepository[stations.Station](
                    mapping=await stations.load_stations(),
                    resolution=8,
                ),
            ).from_search_task,
            internal_exchange_name=app.name,
        )

        await trip_search_consumer.consume()
