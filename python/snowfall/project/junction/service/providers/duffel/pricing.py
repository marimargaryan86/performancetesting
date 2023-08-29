import datetime
import random
from collections.abc import Mapping
from typing import Any

import httpx
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.duffel import (
    cache,
    pricing_adapter,
    pricing_transformer,
)
from snowfall.project.junction.service.providers.duffel.client_factory import (
    DuffelClientFactory,
)
from snowfall.project.junction.service.providers.duffel.config import PricingSettings
from snowfall.project.junction.service.providers.duffel.search.parser import (
    dict_to_private_fares,
)
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient


async def price_quotes(  # noqa: WPS210
    app: application.AsyncApplication[PricingSettings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    rate_limit_client = await app.stack.enter_async_context(
        RateLimitClient(
            app.settings.rate_limiter_grpc_host,
            app.settings.rate_limiter_service_configs["duffel"],
        ),
    )
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            str(random.choice(app.settings.redis_dsn)),  # noqa: S311
            decode_responses=False,
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
        amqp_types.Connection(str(app.settings.amqp_dsn)),
    )
    duffel_client_factory = DuffelClientFactory(
        api_base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        version=app.settings.api_version,
        http_client=http_client,
        rate_limit_client=rate_limit_client,
        resellers_map=app.settings.resellers_map,
    )
    offer_cache = cache.OfferCache(
        client=redis.Client[bytes](redis_connection, prefix=app.name),
    )
    await PriceQuoteConsumer(
        consumer_obj=consumer.Consumer(
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
        adapter_factory=pricing_adapter.PricingAdapterFactory(duffel_client_factory),
        provider_company_id=app.settings.provider_company_id,
        offer_ttl=app.settings.ttl,
        resellers_map=app.settings.resellers_map,
    ).consume()


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        transformer: pricing_transformer.PriceQuoteTransformer,
        adapter_factory: pricing_adapter.PricingAdapterFactory,
        offer_cache: cache.OfferCache,
        provider_company_id: str,
        offer_ttl: datetime.timedelta,
        resellers_map: Mapping[str, Mapping[str, Any]],
    ):
        self._pricing = pricing_adapter
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = stdout.get_logger()
        self._producer = producer_obj
        self._adapter_factory = adapter_factory
        self._transformer = transformer
        self._provider_company_id = provider_company_id
        self._ttl = offer_ttl
        self._resellers_map = resellers_map

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(  # noqa: WPS210
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return
        adapter = self._adapter_factory.for_reseller(amqp_message.body.reseller_id)
        reseller_config = self._resellers_map.get(amqp_message.body.reseller_id)
        private_fares = dict_to_private_fares(
            reseller_config.get("private_fares", {}) if reseller_config else {},
        )

        last_travel_date = offer_details.last_travel_date
        offer = await adapter.refresh_offer(offer_details, private_fares)
        offer_details = cache.OfferDetails(
            offer_id=offer.identifier,
            total_amount=offer.total_amount,
            currency=offer.total_currency,
            passengers=[
                cache.OfferDetailsPassenger(
                    identifier=passenger.identifier,
                    passenger_type=passenger.passenger_type,
                )
                for passenger in offer.passengers
            ],
            doc_required=offer.passenger_identity_documents_required,
            last_travel_date=last_travel_date,
        )

        price_quote_id = await self._cache.store(
            record=offer_details,
            expires_at=datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=self._transformer.to_price_quote(
                    price_quote_id=price_quote_id,
                    offer=await adapter.get_price_quote(offer_details),
                    option_id=amqp_message.body.option_id,
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )
