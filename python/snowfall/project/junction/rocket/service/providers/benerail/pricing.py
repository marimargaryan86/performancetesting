import datetime

from snowfall.project.junction.rocket.service.providers.benerail import (
    adapter,
    cache,
    fare_rules,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.vendor.benerail import client as benerail_client


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
        search_result_cache: cache.OffersCache,
        quote_cache: cache.QuoteCache,
        benerail_adapter: adapter.BenerailAdapter,
        ttl: datetime.timedelta,
        client: benerail_client.BenerailClient,
    ):
        self._consumer = consumer_obj
        self._quote_result_producer = quote_result_producer
        self._search_result_cache = search_result_cache
        self._quote_cache = quote_cache
        self._ttl = ttl
        self._adapter = benerail_adapter
        self._client = client

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.QuoteTask],
    ) -> None:
        offer_details = await self._search_result_cache.fetch(
            message.body.quote.offer_id,
        )

        if not offer_details:
            return
        session_token = string.uuid()

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        get_offer_res = await self._adapter.verify_offer(
            offer_details=offer_details,
            session_token=session_token,
        )

        await self._quote_cache.store(
            cache.QuoteDetails(
                amount=get_offer_res.offer_obj.price.amount,
                currency=get_offer_res.offer_obj.price.currency,
            ),
            expires_at=expires_at,
            key=message.body.quote.id,
        )

        base_price_proto = money.from_string(
            str(get_offer_res.offer_obj.price.amount),
            money.Currency(get_offer_res.offer_obj.price.currency),
        ).protobuf()

        quote_obj = models_pb2.Quote(
            price=base_price_proto,
            required_documents=[
                models_pb2.Quote.Required.REQUIRED_PASSPORT_NUMBER,
            ],
            rules=await fare_rules.get_fare_rules(
                benerail_client=self._client,
                offer_obj=get_offer_res.offer_obj,
            ),
            price_breakdown=[
                models_pb2.PriceBreakdown(
                    price=base_price_proto,
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
