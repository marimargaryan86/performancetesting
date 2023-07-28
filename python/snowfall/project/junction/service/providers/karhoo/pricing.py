import datetime
import random

from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.karhoo import cache, config
from snowfall.stdlib import money, service
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.amqp import types as amqp_types


async def price_quotes(
    app: service.AsyncApplication[config.OfferSettings],
) -> None:
    redis_connection: aioredis.Redis[bytes] = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # noqa: S311
            decode_responses=False,
        ).client(),
    )
    amqp_connection = await app.stack.enter_async_context(
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
        provider_company_id=app.settings.provider_company_id,
    ).consume()


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: amqp_consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        ttl: datetime.timedelta,
        provider_company_id: str,
    ):
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._producer = producer_obj
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

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl

        price_quote_id = await self._cache.store(offer_details, expires_at)

        price_quote_price = money.from_string(
            string_amount=offer_details.price,
            currency=offer_details.currency,
        ).protobuf()

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=price_quote_id,
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(expires_at),
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
