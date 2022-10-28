import datetime
import random
from typing import Sequence

import aioredis
import aiosmtplib
import httpx
import pydantic

from snowfall.project.junction.service.providers.ask2go import (
    adapter,
    airports,
    booking,
    cache,
    consumer,
    criteria,
    notifications,
    transformer,
    validator,
)
from snowfall.stdlib import h3, service
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport import amqp
from snowfall.vendor.ask2go import client

_OFFERS = "offers"


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
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    http_timeout: float = 60.0


class _SearchSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    http_timeout: float = 20.0
    poll_retries_limit: int = 10
    wait_time_between_polling: float = 1


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with httpx.AsyncClient(timeout=app.settings.http_timeout) as http_client:
        async with await amqp.create_connection(
            random.choice(app.settings.amqp_dsn),  # nosec
        ) as connection:
            trip_search_consumer = consumer.TripSearchConsumer(
                consumer=amqp.Consumer(
                    connection=connection,
                    exchange=amqp.Exchange(_OFFERS),
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
                        ask2go_client=ask2go_client,
                        notifier=notifications.SmtpNotifier(
                            smtp_client=aiosmtplib.SMTP(
                                hostname=app.settings.smtp_dsn.host,
                                port=app.settings.smtp_dsn.port,
                                username=app.settings.smtp_dsn.user,
                                password=app.settings.smtp_dsn.password,
                                start_tls=True,
                            ),
                            sender=app.settings.smtp_sender,
                            recipient=app.settings.smtp_recipient,
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
                        exchange=amqp.Exchange(_OFFERS),
                    ),
                    ask2go_adapter=adapter.Ask2GoAdapter(
                        ask2go_client=ask2go_client,
                        offer_validator=validator.OfferValidator(),
                        poll_retries_limit=app.settings.poll_retries_limit,
                        wait_time_between_polling=app.settings.wait_time_between_polling,
                    ),
                    offer_transformer=transformer.OfferTransformer(
                        airport_repository=airports.AirportRepository(
                            airports=await ask2go_client.get_airports(),
                            coordinates=filesystem.PkgLoader(
                                "snowfall.project.junction.service.providers.ask2go.main",
                            ).load("airport_coordinates.json"),
                        ),
                        offer_cache=cache.OfferCache(
                            client=redis.Client[bytes](redis_conn, prefix=app.name),
                        ),
                        offer_ttl=app.settings.ttl,
                    ),
                    redis=redis.Client[bytes](
                        redis=redis_conn,
                        prefix=app.name,
                    ),
                )

                await trip_search_consumer.consume()


async def _get_iata_mapping(
    ask2go_client: client.Ask2GoClient,
) -> list[h3.CoordinatesItem[airports.Airport]]:
    loader = filesystem.PkgLoader(
        "snowfall.project.junction.service.providers.ask2go.main",
    )

    return airports.create_airports_mapping(
        coordinates=loader.load("airport_coordinates.json"),
        airports=await ask2go_client.get_airports(),
    )


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="ask2go")

    entrypoint.enter_with_commands(
        service.Command(
            name=_OFFERS,
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
