from __future__ import annotations

import contextlib
from typing import Any, cast

import pydantic
from redis import asyncio as aioredis

from snowfall.project.junction.provider import airports
from snowfall.project.junction.provider import offers as provider_offers
from snowfall.project.junction.service.providers.duffel import criteria
from snowfall.stdlib import h3, service
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types


class OffersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: pydantic.AnyUrl


async def offers(app: service.Application[OffersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_conn: aioredis.Redis[str] = await stack.enter_async_context(
            aioredis.from_url(
                app.settings.redis_dsn,
                decode_responses=True,
            ).client(),
        )
        connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )

        airport_mapping = airports.AirportRepository(
            airports_data=cast(
                list[dict[str, Any]],
                filesystem.PkgLoader(
                    "snowfall.project.junction.service.providers.duffel.main",
                ).load("airports.json"),
            ),
        ).all_()

        trip_search_consumer = provider_offers.create_trip_offer_search_consumer(
            amqp_connection=connection,
            redis_client=redis.Client(redis_conn, prefix=app.name),
            criteria_generator=criteria.CriteriaGenerator(
                h3_mapping=h3.H3MappingRepository[airports.Airport](
                    mapping=airport_mapping,
                    resolution=7,
                ),
            ).from_search_task,
            internal_exchange_name=app.name,
        )

        await trip_search_consumer.consume()
