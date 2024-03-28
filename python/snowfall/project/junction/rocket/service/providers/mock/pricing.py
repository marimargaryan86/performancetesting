import datetime

from snowfall.project.junction.rocket.service.providers.mock import cache
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.transport.amqp import consumer, producer, types


class QuoteResultProducer(object):
    def __init__(self, producer_obj: producer.Producer, routing_key: str):
        self._producer = producer_obj
        self._routing_key = routing_key

    async def publish(self, message: amqp_pb2.QuoteTaskResult) -> None:
        await self._producer.publish(message, self._routing_key)


class QuoteTaskConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.QuoteTask],
        quote_result_producer: QuoteResultProducer,
        quote_cache: cache.QuoteCache,
        ttl: datetime.timedelta,
    ):
        self._consumer = consumer_obj
        self._quote_result_producer = quote_result_producer
        self._quote_cache = quote_cache
        self._ttl = ttl

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.QuoteTask],
    ) -> None:
        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl

        price = money.from_string("100.00", money.Currency("EUR")).protobuf()

        await self._quote_cache.store(
            cache.MockDetails(
                amount=100,
                currency="EUR",
            ),
            expires_at=expires_at,
            key=message.body.quote.id,
        )

        quote_obj = models_pb2.Quote(
            price=price,
            required_documents=[
                models_pb2.Quote.Required.REQUIRED_PASSPORT_NUMBER,
            ],
            rules=[models_pb2.FareRule(title="Refund rules", body="No refund")],
            price_breakdown=[
                models_pb2.PriceBreakdown(
                    price=money.from_string(
                        "100.00",
                        money.Currency("EUR"),
                    ).protobuf(),
                    breakdown_type=models_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE,
                ),
            ],
        )

        quote_obj.MergeFrom(message.body.quote)

        await self._quote_result_producer.publish(
            amqp_pb2.QuoteTaskResult(
                quote=quote_obj,
                reseller_id=message.body.reseller_id,
            ),
        )
