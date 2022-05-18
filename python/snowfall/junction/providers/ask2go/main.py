import datetime
import random
from typing import Sequence

import aioredis
import aiosmtplib
import httpx
import pydantic

from snowfall.junction.providers.ask2go import (
    adapter,
    airports,
    booking,
    cache,
    consumer,
    criteria,
    h3,
    transformer,
    validator,
)
from snowfall.stdlib import service
from snowfall.stdlib.persistence import filesystem, redis
from snowfall.stdlib.transport import amqp
from snowfall.vendor.ask2go import client


class _OffersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    http_timeout: float = 20.0


class _OrdersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    http_timeout: float = 60.0


class _SearchSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    http_timeout: float = 20.0


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with httpx.AsyncClient(timeout=app.settings.http_timeout) as http_client:
        async with await amqp.create_connection(
            random.choice(app.settings.amqp_dsn),  # nosec
        ) as connection:
            trip_search_consumer = consumer.TripSearchConsumer(
                consumer=amqp.Consumer(
                    connection=connection,
                    exchange=amqp.Exchange("offers"),
                    queue_name="{0}_offers".format(app.name),
                    routing_key="offers.search.trip",
                ),
                producer=amqp.Producer(
                    connection=connection,
                    exchange=amqp.Exchange("ask2go"),
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
        decode_responses=False,
    ).client() as redis_conn:
        async with httpx.AsyncClient(timeout=app.settings.http_timeout) as http_client:
            ask2go_client = client.Ask2GoClient(
                api_base_url=app.settings.api_base_url,
                api_booking_base_url=app.settings.api_booking_base_url,
                http_client=http_client,
            )

            async with await amqp.create_connection(
                random.choice(app.settings.amqp_dsn),  # nosec
            ) as connection:
                await consumer.OrderConsumer(
                    consumer=amqp.Consumer(
                        connection=connection,
                        exchange=amqp.Exchange("orders"),
                        queue_name="{0}_orders".format(app.name),
                        routing_key="orders.offers",
                    ),
                    producer=amqp.Producer(
                        connection=connection,
                        exchange=amqp.Exchange("orders"),
                    ),
                    booking_handler=booking.BookingHandler(
                        a2g_client=ask2go_client,
                        smtp_client=aiosmtplib.SMTP(
                            hostname=app.settings.smtp_dsn.host,
                            port=app.settings.smtp_dsn.port,
                            username=app.settings.smtp_dsn.user,
                            password=app.settings.smtp_dsn.password,
                            start_tls=True,
                        ),
                    ),
                    offer_cache=cache.OfferCache(
                        client=redis.Client[bytes](redis_conn, prefix=app.name),
                    ),
                ).consume()


async def _searches(app: service.Application[_SearchSettings]) -> None:
    async with aioredis.from_url(
        random.choice(app.settings.redis_dsn),  # nosec
        decode_responses=False,
    ).client() as redis_conn:
        async with httpx.AsyncClient(timeout=app.settings.http_timeout) as http_client:
            ask2go_client = client.Ask2GoClient(
                api_base_url=app.settings.api_base_url,
                api_booking_base_url=app.settings.api_booking_base_url,
                http_client=http_client,
            )
            async with await amqp.create_connection(
                random.choice(app.settings.amqp_dsn),  # nosec
            ) as connection:
                trip_search_consumer = consumer.SearchCriteriaConsumer(
                    consumer=amqp.Consumer(
                        connection=connection,
                        exchange=amqp.Exchange("ask2go"),
                        queue_name="{0}_searches".format(app.name),
                        routing_key="offers.search.trip",
                    ),
                    producer=amqp.Producer(
                        connection=connection,
                        exchange=amqp.Exchange("offers"),
                    ),
                    a2g_client=adapter.Ask2GoAdapter(
                        ask2go_client=ask2go_client,
                        offer_validator=validator.OfferValidator(),
                    ),
                    offer_transformer=transformer.OfferTransformer(
                        airport_repository=airports.AirportRepository(
                            airports=await ask2go_client.get_airports(),
                            coordinates=filesystem.PkgLoader(
                                "snowfall.junction.providers.ask2go.main",
                            ).load("airport_coordinates.json"),
                        ),
                        offer_cache=cache.OfferCache(
                            client=redis.Client[bytes](redis_conn, prefix=app.name),
                        ),
                        offer_ttl=app.settings.ttl,
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
