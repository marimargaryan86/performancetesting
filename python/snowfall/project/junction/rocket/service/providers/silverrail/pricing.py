import datetime

import timezonefinder

from snowfall.project.junction.rocket.service.providers.silverrail import adapter, cache
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, producer, types

_tz_finder = timezonefinder.TimezoneFinder()


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
        result_detail_cache: cache.ResultDetailCache,
        quote_cache: cache.QuoteCache,
        ttl: datetime.timedelta,
        offer_matcher: adapter.SilverrailOfferMatcher,
        pay_company_id: str,
    ):
        self._consumer = consumer_obj
        self._quote_result_producer = quote_result_producer
        self._result_detail_cache = result_detail_cache
        self._quote_cache = quote_cache
        self._ttl = ttl
        self._offer_matcher = offer_matcher
        self._pay_company_id = pay_company_id
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.QuoteTask],
    ) -> None:
        for offer_id in message.body.quote.offer_ids:
            selected_offer = await self._result_detail_cache.fetch(offer_id)

            if not selected_offer:
                return

            matched_offer = await self._offer_matcher.get_matching_offer(
                selected_offer,
            )

            expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
            ptp_price = matched_offer.ptp_price

            await self._quote_cache.store(
                record=cache.PriceQuote(
                    leg_solution=matched_offer.leg_solution,
                    ptp_price=ptp_price,
                    passengers=matched_offer.passengers,
                ),
                expires_at=expires_at,
                key=message.body.quote.id,
            )
            if ptp_price.total_price is None:
                self._logger.error(
                    "No pricing information in Silverrail response",
                )
                return
            if ptp_price.ticketable_fares is None:
                self._logger.error(
                    "No fare information in Silverrail response",
                )
                return

            price = self._offer_matcher.convert_total_price(
                ptp_price.total_price,
            )
            quote_obj = models_pb2.Quote(
                pay_company_id=self._pay_company_id,
                expires_at=protobuf.datetime_to_protobuf(expires_at),
                total_price=price,
                quoted_offers=[
                    models_pb2.QuotedOffer(
                        offer_id=offer_id,
                        price=price,
                        price_breakdown=self._offer_matcher.convert_price_breakdown(
                            ptp_price.ticketable_fares,
                        ),
                        rules=[
                            models_pb2.FareRule(
                                title=rule.category or "",
                                body=rule.description or "",
                            )
                            for rule in self._offer_matcher.get_fare_rules(ptp_price)
                            if rule.category or rule.description
                        ],
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
