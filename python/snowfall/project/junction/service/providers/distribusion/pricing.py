import contextlib
import random
import uuid

import structlog
from redis import asyncio as aioredis

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.distribusion import cache
from snowfall.project.junction.service.providers.distribusion.config import (
    SearchesSettings,
)
from snowfall.stdlib import money, service
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, types


async def price_quotes(
    app: service.Application[SearchesSettings],
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            types.Connection(app.settings.amqp_dsn),
        )
        offer_cache = cache.OffersCache(
            client=redis.Client[bytes](redis_connection, prefix=app.name),
        )
        await PriceQuoteConsumer(
            consumer_obj=consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_prices".format(app.name),
                binds=[(types.Exchange("prices"), "offers.pricing")],
            ),
            producer_obj=producer.Producer(
                connection=amqp_connection,
                exchange=types.Exchange("prices"),
            ),
            offer_cache=offer_cache,
        ).consume()


class PriceQuoteConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
    ):
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=str(uuid.uuid4()),
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(offer_details.expires_at),
                    price=money.Money(
                        amount=offer_details.price,
                        currency=money.Currency(offer_details.currency),
                    ).protobuf(),
                ),
            ),
            routing_key="offers.result.price",
        )
