import contextlib
import random
import uuid

import structlog
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.go.service.offers.v1alpha import models_pb2 as offers_pb2
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
            provider_company_id=app.settings.provider_company_id,
        ).consume()


class PriceQuoteConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        provider_company_id: str,
    ):
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj
        self._provider_company_id = provider_company_id

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
                    rules=[
                        offers_pb2.FareRule(
                            title=fare_rule.name,
                            body=fare_rule.description,
                        )
                        for fare_rule in offer_details.fare_rules or []
                    ],
                    penalties=self._create_penalties(offer_details),
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )

    def _create_penalties(
        self,
        offer_details: cache.OfferDetails,
    ) -> list[offers_pb2.Penalty]:
        res = []

        if offer_details.fully_refundable:
            res.append(
                offers_pb2.Penalty(
                    penalty_type=offers_pb2.Penalty.Type.TYPE_REFUND,
                    refundable=True,
                    applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
                ),
            )

        if offer_details.non_refundable:
            res.append(
                offers_pb2.Penalty(
                    penalty_type=offers_pb2.Penalty.Type.TYPE_REFUND,
                    refundable=False,
                    applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
                ),
            )

        if offer_details.changeable:
            res.append(
                offers_pb2.Penalty(
                    penalty_type=offers_pb2.Penalty.Type.TYPE_EXCHANGE,
                    changeable=True,
                    applicability=offers_pb2.Penalty.Applicability.APPLICABILITY_BEFORE,
                ),
            )

        return res
