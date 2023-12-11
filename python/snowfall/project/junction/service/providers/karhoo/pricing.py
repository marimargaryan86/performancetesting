import datetime

import httpx

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.karhoo import adapter, cache, config
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import amqp_factory, application, redis_factory
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.karhoo import client


async def price_quotes(
    app: application.Application[config.OfferSettings],
) -> None:
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=False,
    )
    amqp_connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    producer_obj = producer.Producer(
        connection=amqp_connection,
        exchange=amqp_types.Exchange("prices"),
    )
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout.seconds,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    karhoo_client = client.KarhooClient(
        api_key=app.settings.api_key,
        base_url=str(app.settings.api_base_url),
        http_client=http_client,
    )
    await PriceQuoteConsumer(
        consumer_obj=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_prices".format(app.name),
            binds=[(amqp_types.Exchange("prices"), "offers.pricing")],
        ),
        producer_obj=producer_obj,
        offer_cache=cache.OffersCache(
            client=redis_client,
        ),
        pricing_cache=cache.PricingCache(
            client=redis_client,
        ),
        ttl=app.settings.ttl,
        provider_company_id=app.settings.provider_company_id,
        offer_matcher=adapter.KarhooOfferMatcher(
            karhoo_client=karhoo_client,
            ttl=app.settings.ttl,
        ),
    ).consume()


class PriceQuoteConsumer(object):
    def __init__(
        self,
        consumer_obj: amqp_consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        pricing_cache: cache.PricingCache,
        ttl: datetime.timedelta,
        provider_company_id: str,
        offer_matcher: adapter.KarhooOfferMatcher,
    ):
        self._cache = offer_cache
        self._pricing_cache = pricing_cache
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._logger = stdout.get_logger()
        self._ttl = ttl
        self._provider_company_id = provider_company_id
        self._offer_matcher = offer_matcher

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        try:
            price_quote = await self._offer_matcher.create_matching_price_quote(
                offer_details,
            )
        except errors.HttpError:
            self._logger.exception(
                "Failed while retrieving offer",
                offer_details=offer_details.dict(),
            )
            return

        if price_quote is None:
            self._logger.error(
                "Failed to match offer",
                offer_details=offer_details.dict(),
            )
            return

        price_quote_id = await self._pricing_cache.store(
            price_quote,
            price_quote.expires_at,
        )

        price_quote_price = money.from_string(
            string_amount=price_quote.price,
            currency=price_quote.currency,
        ).protobuf()

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=price_quote_id,
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(
                        price_quote.expires_at,
                    ),
                    price=price_quote_price,
                    price_breakdown=[
                        offers_pb2.PriceBreakdown(
                            price=price_quote_price,
                            breakdown_type=offers_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                    penalties=[],
                    required_documents=[],
                    rules=[],
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )
