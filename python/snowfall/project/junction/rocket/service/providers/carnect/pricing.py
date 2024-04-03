import datetime

from snowfall.project.junction.rocket.service.providers.carnect import cache
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
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
        ttl: datetime.timedelta,
    ):
        self._consumer = consumer_obj
        self._quote_result_producer = quote_result_producer
        self._search_result_cache = search_result_cache
        self._ttl = ttl

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.QuoteTask],
    ) -> None:
        offer_cache = await self._search_result_cache.fetch(message.body.quote.offer_id)

        if not offer_cache:
            return

        quote_obj = models_pb2.Quote()

        await self._quote_result_producer.publish(
            amqp_pb2.QuoteTaskResult(
                quote=quote_obj,
                reseller_id=message.body.reseller_id,
            ),
        )
