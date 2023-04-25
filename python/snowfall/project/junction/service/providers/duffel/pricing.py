import contextlib
import datetime
import random

import httpx
import structlog
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.service.providers.duffel import (
    cache,
    pricing_adapter,
    pricing_transformer,
)
from snowfall.project.junction.service.providers.duffel.config import PricingSettings
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.duffel import client


async def price_quotes(  # noqa: WPS210
    app: service.Application[PricingSettings],
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                timeout=app.settings.http_timeout,
            ),
        )
        logging.register(http_client)
        metrics.register(http_client)
        redis_connection: aioredis.Redis[bytes] = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            amqp_types.Connection(app.settings.amqp_dsn),
        )
        duffel_client = client.DuffelClient(
            api_base_url=app.settings.api_base_url,
            api_key=app.settings.api_key,
            version=app.settings.api_version,
            http_client=http_client,
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
            adapter=pricing_adapter.PricingAdapter(duffel_client=duffel_client),
            provider_company_id=app.settings.provider_company_id,
            offer_ttl=app.settings.ttl,
        ).consume()


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: amqp_consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        transformer: pricing_transformer.PriceQuoteTransformer,
        adapter: pricing_adapter.PricingAdapter,
        offer_cache: cache.OfferCache,
        provider_company_id: str,
        offer_ttl: datetime.timedelta,
    ):
        self._pricing = pricing_adapter
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj
        self._adapter = adapter
        self._transformer = transformer
        self._provider_company_id = provider_company_id
        self._ttl = offer_ttl

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        price_quote_id = await self._cache.store(
            record=offer_details,
            expires_at=datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
        )

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=self._transformer.to_price_quote(
                    price_quote_id=price_quote_id,
                    offer=await self._adapter.get_price_quote(offer_details),
                    option_id=amqp_message.body.option_id,
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )
