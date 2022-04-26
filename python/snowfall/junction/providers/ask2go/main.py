import datetime
import random
from typing import Sequence

import aioredis
import httpx
import pydantic

from snowfall.junction.providers.ask2go import (
    adapter,
    airports,
    cache,
    consumer,
    criteria,
    h3,
)
from snowfall.stdlib import service
from snowfall.stdlib.persistence import filesystem, redis
from snowfall.stdlib.transport import amqp
from snowfall.vendor.ask2go import client


class _OffersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl


class _OrdersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]


class _SearchSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with httpx.AsyncClient() as http_client:
        async with amqp.Connection(
            random.choice(app.settings.amqp_dsn),  # nosec
        ) as connection:
            trip_search_consumer = consumer.TripSearchConsumer(
                consumer=await amqp.create_consumer(
                    conn=connection,
                    exchange_name="offers",
                    queue_name="{0}_offers".format(app.name),
                    routing_key="offers.search.trip",
                ),
                producer=await amqp.create_producer(
                    conn=connection,
                    exchange_name="ask2go",
                ),
                generator=criteria.CriteriaGenerator(
                    h3_mapping=h3.H3MappingRepository[airports.Airport](
                        mapping=await _get_iata_mapping(
                            ask2go_client=client.Ask2GoClient(
                                api_base_url=app.settings.api_base_url,
                                api_booking_base_url=app.settings.api_booking_base_url,
                                http_client=http_client,
                            ),
                        ),
                        resolution=7,
                    ),
                ),
            )

            await trip_search_consumer.consume()


async def _orders(app: service.Application[_OrdersSettings]) -> None:
    async with aioredis.from_url(
        random.choice(app.settings.redis_dsn),  # nosec
        decode_responses=True,
    ).client() as redis_conn:
        async with httpx.AsyncClient() as http_client:
            ask2go_client = client.Ask2GoClient(
                api_base_url=app.settings.api_base_url,
                api_booking_base_url=app.settings.api_booking_base_url,
                http_client=http_client,
            )

            async with amqp.Connection(
                random.choice(app.settings.amqp_dsn),  # nosec
            ) as connection:
                trip_search_consumer = consumer.OrderConsumer(
                    consumer=await amqp.create_consumer(
                        conn=connection,
                        exchange_name="orders",
                        queue_name="{0}_offers".format(app.name),
                        routing_key="orders.offers",
                    ),
                    producer=await amqp.create_producer(
                        conn=connection,
                        exchange_name="orders",
                    ),
                    a2g_client=ask2go_client,
                    offer_cache=cache.OfferCache(
                        client=redis.Client[str](redis_conn),
                    ),
                )

                await trip_search_consumer.consume()


async def _searches(app: service.Application[_SearchSettings]) -> None:
    async with aioredis.from_url(
        random.choice(app.settings.redis_dsn),  # nosec
        decode_responses=True,
    ).client() as redis_conn:
        async with httpx.AsyncClient() as http_client:
            ask2go_client = client.Ask2GoClient(
                api_base_url=app.settings.api_base_url,
                api_booking_base_url=app.settings.api_booking_base_url,
                http_client=http_client,
            )
            async with amqp.Connection(
                random.choice(app.settings.amqp_dsn),  # nosec
            ) as connection:
                trip_search_consumer = consumer.SearchCriteriaConsumer(
                    consumer=await amqp.create_consumer(
                        conn=connection,
                        exchange_name="ask2go",
                        queue_name="{0}_search".format(app.name),
                        routing_key="offers.search.trip",
                    ),
                    producer=await amqp.create_producer(
                        conn=connection,
                        exchange_name="offers",
                    ),
                    a2g_client=adapter.Ask2GoAdapter(
                        ask2go_client=ask2go_client,
                        airport_repository=airports.AirportRepository(
                            airports=await ask2go_client.get_airports(),
                            coordinates=filesystem.PkgLoader(
                                "snowfall.junction.providers.ask2go.main",
                            ).load("airport_coordinates.json"),
                        ),
                        offer_cache=cache.OfferCache(
                            client=redis.Client[str](redis_conn),
                        ),
                        ttl=app.settings.ttl,
                    ),
                )

                await trip_search_consumer.consume()


async def _get_iata_mapping(
    ask2go_client: client.Ask2GoClient,
) -> list[h3.CoordinatesItem[airports.Airport]]:
    loader = filesystem.PkgLoader("snowfall.junction.providers.ask2go.main")

    return airports.create_airports_mapping(
        coordinates=loader.load("airport_coordinates.json"),
        airports=await ask2go_client.get_airports(),
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="ask2go")

    entrypoint.enter_with_commands(
        service.Command(
            name="offers",
            callback=_offers,
            settings_class=_OffersSettings,
        ),
        service.Command(
            name="orders",
            callback=_orders,
            settings_class=_OrdersSettings,
        ),
        service.Command(
            name="searches",
            callback=_searches,
            settings_class=_SearchSettings,
        ),
    )
