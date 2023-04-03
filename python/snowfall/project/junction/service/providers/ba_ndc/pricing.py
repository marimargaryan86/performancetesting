import contextlib
import random

import structlog
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.service.providers.ba_ndc import (
    cache,
    config,
    pricing_transformer,
)
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.amqp import types as amqp_types


async def price_quotes(
    app: service.Application[config.PricingSettings],
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
        offer_cache = cache.OfferCache(
            client=redis.Client[bytes](redis_connection, prefix=app.name),
        )
        await PriceQuoteConsumer(
            consumer_obj=amqp_consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_prices".format(app.name),
                binds=[(amqp_types.Exchange("prices"), "offers.pricing")],
            ),
            producer_obj=producer.Producer(
                connection=amqp_connection,
                exchange=amqp_types.Exchange("prices"),
            ),
            offer_cache=offer_cache,
            transformer=pricing_transformer.PriceQuoteTransformer(
                offer_cache=offer_cache,
            ),
            provider_company_id=app.settings.provider_company_id,
        ).consume()


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: amqp_consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        transformer: pricing_transformer.PriceQuoteTransformer,
        offer_cache: cache.OfferCache,
        provider_company_id: str,
    ):
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj
        self._transformer = transformer
        self._provider_company_id = provider_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=self._transformer.to_price_quote(
                    offer_details=offer_details,
                    option_id=amqp_message.body.option_id,
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )
