import contextlib
import datetime
import random

import structlog
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.karhoo import cache, config
from snowfall.stdlib import money, service, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.amqp import types as amqp_types


async def price_quotes(
    app: service.Application[config.OfferSettings],
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            amqp_types.Connection(app.settings.amqp_dsn),
        )
        producer_obj = producer.Producer(
            connection=amqp_connection,
            exchange=amqp_types.Exchange("prices"),
        )

        await PriceQuoteConsumer(
            consumer_obj=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_prices".format(app.name),
                binds=[(amqp_types.Exchange("prices"), "offers.pricing")],
            ),
            producer_obj=producer_obj,
            offer_cache=cache.OffersCache(
                client=redis.Client(redis_connection, prefix=app.name),
            ),
            ttl=app.settings.ttl,
        ).consume()


class PriceQuoteConsumer(object):
    def __init__(
        self,
        consumer_obj: amqp_consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        ttl: datetime.timedelta,
    ):
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._logger = structlog.get_logger(__name__)
        self._ttl = ttl

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=string.uuid(),
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(expires_at),
                    price=money.from_string(
                        string_amount=offer_details.price,
                        currency=offer_details.currency,
                    ).protobuf(),
                    penalties=[],
                    required_documents=[],
                    rules=[],
                ),
            ),
            routing_key="offers.result.price",
        )
