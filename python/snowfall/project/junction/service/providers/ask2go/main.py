import contextlib
import datetime
import random
from typing import Any, Sequence, cast

import aioredis
import aiosmtplib
import httpx
import pydantic

from snowfall.project.junction.provider import status
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
from snowfall.stdlib.instrumentation import httpx_metrics
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer, trackable, types
from snowfall.vendor.ask2go import client

_OFFERS = "offers"


class _OffersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: pydantic.AnyUrl


class _OrdersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr
    http_timeout: float = 60.0


class _SearchSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    http_timeout: float = 20.0
    poll_retries_limit: int = 10
    wait_time_between_polling: float = 1


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_conn = await stack.enter_async_context(
            aioredis.from_url(
                app.settings.redis_dsn,
                decode_responses=True,
            ).client(),
        )
        connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )

        trip_search_consumer = consumer.TripSearchConsumer(
            consumer_obj=amqp_consumer.Consumer(
                connection=connection,
                queue_name="{0}_offers".format(app.name),
                binds=[
                    (types.Exchange(_OFFERS), "offers.search.trip"),
                    (
                        types.Exchange("ask2go"),
                        trackable.to_tracking_key("offers.search.trip"),
                    ),
                ],
            ),
            producer_obj=trackable.TrackableProducer(
                producer.Producer(
                    connection=connection,
                    exchange=types.Exchange("ask2go"),
                ),
            ),
            generator=criteria.CriteriaGenerator(
                h3_mapping=h3.H3MappingRepository[airports.Airport](
                    mapping=airports.AirportRepository(
                        airports_data=cast(
                            list[dict[str, Any]],
                            filesystem.PkgLoader(
                                "snowfall.project.junction.service.providers.ask2go.main",
                            ).load("airports.json"),
                        ),
                    ).all_(),
                    resolution=7,
                ),
            ),
            status_handler=status.SubtaskStatusHandler(
                reporter=trackable.StatusReporter(
                    producer.Producer(
                        connection=connection,
                        exchange=types.Exchange(_OFFERS),
                    ),
                ),
                redis=redis.Client[str](redis_conn, prefix=app.name),
                trackable_key=trackable.to_tracking_key("offers.search.trip"),
            ),
        )

        await trip_search_consumer.consume()


async def _orders(app: service.Application[_OrdersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx_metrics.with_metrics(
                httpx.AsyncClient(
                    timeout=app.settings.http_timeout,
                ),
            ),
        )
        redis_connection = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        ask2go_client = client.Ask2GoClient(
            api_base_url=app.settings.api_base_url,
            api_booking_base_url=app.settings.api_booking_base_url,
            http_client=http_client,
        )

        await consumer.OrderConsumer(
            consumer_obj=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_orders".format(app.name),
                binds=[(types.Exchange("orders"), "orders.offers")],
            ),
            producer_obj=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange("orders"),
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
                client=redis.Client[bytes](redis_connection, prefix=app.name),
            ),
        ).consume()


async def _searches(app: service.Application[_SearchSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx_metrics.with_metrics(
                httpx.AsyncClient(
                    timeout=app.settings.http_timeout,
                ),
            ),
        )
        redis_connection = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        ask2go_client = client.Ask2GoClient(
            api_base_url=app.settings.api_base_url,
            api_booking_base_url=app.settings.api_booking_base_url,
            http_client=http_client,
        )

        await consumer.SearchCriteriaConsumer(
            consumer_obj=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_searches".format(app.name),
                binds=[(types.Exchange("ask2go"), "offers.search.trip")],
                middlewares=[
                    trackable.ReportingMiddleware(
                        status_reporter=trackable.StatusReporter(
                            producer=producer.Producer(
                                connection=amqp_connection,
                                exchange=types.Exchange("ask2go"),
                            ),
                        ),
                    ),
                ],
            ),
            producer_obj=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange(_OFFERS),
            ),
            ask2go_adapter=adapter.Ask2GoAdapter(
                ask2go_client=ask2go_client,
                offer_validator=validator.OfferValidator(),
                poll_retries_limit=app.settings.poll_retries_limit,
                wait_time_between_polling=app.settings.wait_time_between_polling,
            ),
            offer_transformer=transformer.OfferTransformer(
                airport_repository=airports.AirportRepository(
                    airports_data=cast(
                        list[dict[str, Any]],
                        filesystem.PkgLoader(
                            "snowfall.project.junction.service.providers.ask2go.main",
                        ).load("airports.json"),
                    ),
                ),
                offer_cache=cache.OfferCache(
                    client=redis.Client[bytes](redis_connection, prefix=app.name),
                ),
                offer_ttl=app.settings.ttl,
            ),
            redis=redis.Client[bytes](
                redis=redis_connection,
                prefix=app.name,
            ),
        ).consume()


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
