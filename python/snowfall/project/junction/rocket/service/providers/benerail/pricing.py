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
from snowfall.stdlib.format import protobuf
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
        pay_company_id: str,
    ):
        self._consumer = consumer_obj
        self._quote_result_producer = quote_result_producer
        self._search_result_cache = search_result_cache
        self._quote_cache = quote_cache
        self._ttl = ttl
        self._adapter = benerail_adapter
        self._client = client
        self._pay_company_id = pay_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.QuoteTask],
    ) -> None:
        quoted_offers: list[models_pb2.QuotedOffer] = []
        for offer_id in message.body.quote.offer_ids:
            offer_details = await self._search_result_cache.fetch(
                offer_id,
            )

            if not offer_details:
                return

            session_token = string.uuid()
            get_offer_res = await self._adapter.verify_offer(
                offer_details=offer_details,
                session_token=session_token,
            )

            base_price_proto = money.from_string(
                str(get_offer_res.offer_obj.price.amount),
                money.Currency(get_offer_res.offer_obj.price.currency),
            ).protobuf()

            quoted_offers.append(
                models_pb2.QuotedOffer(
                    offer_id=offer_id,
                    price=base_price_proto,
                    required_documents=[
                        models_pb2.QuotedOffer.Required.REQUIRED_PASSPORT_NUMBER,
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
                ),
            )

        total_price = money.total([
            money.from_protobuf(offer.price) for offer in quoted_offers
        ])
        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        await self._quote_cache.store(
            cache.QuoteDetails(
                amount=total_price.amount,
                currency=total_price.currency.code,
            ),
            expires_at=expires_at,
            key=message.body.quote.id,
        )

        quote_obj = models_pb2.Quote(
            pay_company_id=self._pay_company_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            total_price=total_price.protobuf(),
            quoted_offers=quoted_offers,
        )

        quote_obj.MergeFrom(message.body.quote)

        await self._quote_result_producer.publish(
            amqp_pb2.QuoteTaskResult(
                quote=quote_obj,
                reseller_id=message.body.reseller_id,
            ),
        )
