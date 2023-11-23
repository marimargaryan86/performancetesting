import datetime
from collections.abc import Mapping
from typing import Any

import httpx

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
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    redis_factory,
)
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.rate_limiter import gubernator_pb2_grpc
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient


async def price_quotes(
    app: application.Application[PricingSettings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.http_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    rate_limit_client = RateLimitClient(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["duffel"],
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    duffel_client_factory = DuffelClientFactory(
        api_base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        version=app.settings.api_version,
        http_client=http_client,
        rate_limit_client=rate_limit_client,
        resellers_map=app.settings.resellers_map,
    )
    offer_cache = cache.OfferCache(
        client=redis_client,
    )
    price_quote_cache = cache.PriceQuoteCache(client=redis_client)

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
        price_quote_cache=price_quote_cache,
        transformer=pricing_transformer.PriceQuoteTransformer(
            offer_cache=offer_cache,
        ),
        adapter_factory=pricing_adapter.PricingAdapterFactory(duffel_client_factory),
        provider_company_id=app.settings.provider_company_id,
        offer_ttl=app.settings.ttl,
        resellers_map=app.settings.resellers_map,
    ).consume()


class PriceQuoteConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        transformer: pricing_transformer.PriceQuoteTransformer,
        adapter_factory: pricing_adapter.PricingAdapterFactory,
        offer_cache: cache.OfferCache,
        price_quote_cache: cache.PriceQuoteCache,
        provider_company_id: str,
        offer_ttl: datetime.timedelta,
        resellers_map: Mapping[str, Mapping[str, Any]],
    ):
        self._pricing = pricing_adapter
        self._offer_cache = offer_cache
        self._price_quote_cache = price_quote_cache
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

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._offer_cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        adapter = self._adapter_factory.for_reseller(amqp_message.body.reseller_id)

        reseller_config = self._resellers_map.get(amqp_message.body.reseller_id)

        private_fares = dict_to_private_fares(
            reseller_config.get("private_fares", {}) if reseller_config else {},
        )

        offer = await adapter.refresh_offer(offer_details, private_fares)

        price_quote = cache.PriceQuote(
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
            last_travel_date=offer_details.last_travel_date,
        )

        price_quote_id = await self._price_quote_cache.store(
            record=price_quote,
            expires_at=datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=self._transformer.to_price_quote(
                    price_quote_id=price_quote_id,
                    offer=offer,
                    option_id=amqp_message.body.option_id,
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )
