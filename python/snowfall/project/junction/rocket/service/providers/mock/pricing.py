import datetime

from snowfall.project.junction.rocket.service.providers.mock import cache
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import consumer, producer, types


class QuoteResultProducer:
    def __init__(self, producer_obj: producer.Producer, routing_key: str):
        self._producer = producer_obj
        self._routing_key = routing_key

    async def publish(self, message: amqp_pb2.QuoteTaskResult) -> None:
        await self._producer.publish(message, self._routing_key)


class QuoteTaskConsumer:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.QuoteTask],
        quote_result_producer: QuoteResultProducer,
        search_result_cache: cache.SearchResultCache,
        quote_cache: cache.QuoteCache,
        ttl: datetime.timedelta,
        pay_company_id: str,
    ):
        self._consumer = consumer_obj
        self._quote_result_producer = quote_result_producer
        self._search_result_cache = search_result_cache
        self._quote_cache = quote_cache
        self._ttl = ttl
        self._pay_company_id = pay_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.QuoteTask],
    ) -> None:
        quoted_offers: list[models_pb2.QuotedOffer] = []
        for offer_id in message.body.quote.offer_ids:
            offer_cache = await self._search_result_cache.fetch(offer_id)

            if not offer_cache:
                return

            base_price = money.from_string(
                str(offer_cache.amount),
                money.Currency(offer_cache.currency),
            ).protobuf()

            quoted_offer = models_pb2.QuotedOffer(
                offer_id=offer_id,
                price=base_price,
                required_documents=[
                    models_pb2.QuotedOffer.Required.REQUIRED_PASSPORT_NUMBER,
                ],
                rules=[models_pb2.FareRule(title="Refund rules", body="No refund")],
                price_breakdown=[
                    models_pb2.PriceBreakdown(
                        price=base_price,
                        breakdown_type=models_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE,
                    ),
                ],
            )

            quoted_offers.append(quoted_offer)

        total_price = money.total([
            money.from_protobuf(offer.price) for offer in quoted_offers
        ])

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl

        await self._quote_cache.store(
            cache.MockDetails(
                amount=total_price.amount,
                currency=total_price.currency.code,
            ),
            expires_at=expires_at,
            key=message.body.quote.id,
        )

        quote_obj = models_pb2.Quote(
            pay_company_id=self._pay_company_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            quoted_offers=quoted_offers,
            total_price=total_price.protobuf(),
        )
        quote_obj.MergeFrom(message.body.quote)

        await self._quote_result_producer.publish(
            amqp_pb2.QuoteTaskResult(
                quote=quote_obj,
                reseller_id=message.body.reseller_id,
            ),
        )
