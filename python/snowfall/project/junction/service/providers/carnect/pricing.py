import datetime

import httpx

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.carnect import adapter, cache, config
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import amqp_factory, application, redis_factory
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.carnect.client import CarnectClient
from snowfall.vendor.carnect.config import Config


async def price_quotes(
    app: application.Application[config.PricingSettings],
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

    carnect_config = Config(
        timeout=app.settings.ttl.seconds,
        base_url=str(app.settings.api_base_url),
        export_soap_requests=True,
        username=app.settings.api_username,
        password=app.settings.api_password,
        is_test=app.settings.is_test,
    )

    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout.seconds,
        ),
    )

    client = CarnectClient(http_client=http_client, config=carnect_config)

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
        offer_matcher=adapter.CarnectOfferMatcher(
            carnect_client=client,
            carnect_config=carnect_config,
        ),
        ttl=app.settings.ttl,
        provider_company_id=app.settings.provider_company_id,
    ).consume()


class PriceQuoteConsumer:
    def __init__(
        self,
        consumer_obj: amqp_consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        pricing_cache: cache.PricingCache,
        offer_matcher: adapter.CarnectOfferMatcher,
        ttl: datetime.timedelta,
        provider_company_id: str,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._cache = offer_cache
        self._pricing_cache = pricing_cache
        self._offer_matcher = offer_matcher
        self._logger = stdout.get_logger()
        self._ttl = ttl
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

        quote_result = await self._offer_matcher.get_matching_quote(offer_details)

        if quote_result is None:
            self._logger.error(
                "Failed to match offer",
                offer_details=offer_details.dict(),
            )
            return

        try:
            quote_id = quote_result.veh_avail_core.reference.id_context  # type: ignore[union-attr]
        except AttributeError:
            self._logger.exception(
                "Failed to get quote id",
                offer_details=offer_details.dict(),
            )
            return

        if quote_id is None:
            self._logger.error(
                "Quote id is missing",
                offer_details=offer_details.dict(),
            )
            return

        price_quote = cache.PriceQuote(
            quote_id=quote_id,
        )

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        price_quote_id = await self._pricing_cache.store(
            record=price_quote,
            expires_at=expires_at,
        )

        offer_price = adapter.get_offer_price(quote_result).protobuf()

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=price_quote_id,
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(expires_at),
                    price=offer_price,
                    price_breakdown=[
                        offers_pb2.PriceBreakdown(
                            price=offer_price,
                            breakdown_type=offers_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                    conditional_prices=adapter.get_conditional_prices(
                        veh_avail=quote_result,
                    ),
                    rules=adapter.get_fare_rules(quote_result),
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )
