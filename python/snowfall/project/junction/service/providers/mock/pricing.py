import datetime

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.mock import cache
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types

_RULE_TITLE = "FAKE FARE RULE"
_RULE_BODY = "THIS PRICE QUOTE IS NOT GENUINE. IT ORIGINATES FROM THE MOCK PROVIDER"


class Quoter:
    def __init__(
        self,
        option_cache: cache.OptionCache,
        price_quote_cache: cache.PriceQuoteCache,
        ttl: datetime.timedelta,
    ):
        self._option_cache = option_cache
        self._price_quote_cache = price_quote_cache
        self._ttl = ttl

    async def generate_quote(self, option_id: str) -> offers_pb2.PriceQuote:
        offer_details = await self._option_cache.fetch(option_id)

        if not offer_details:
            raise cache.OptionNotFoundError()

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        price = money.Money(
            amount=offer_details.amount,
            currency=money.Currency(offer_details.currency),
        )

        return offers_pb2.PriceQuote(
            id=await self._price_quote_cache.store(
                cache.MockDetails(
                    amount=price.amount,
                    currency=price.currency.code,
                ),
                expires_at=expires_at,
            ),
            option_id=option_id,
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            price=price.protobuf(),
            rules=[
                offers_pb2.FareRule(
                    title=_RULE_TITLE,
                    body=_RULE_BODY,
                ),
            ],
        )


class Consumer:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        quoter: Quoter,
        provider_company_id: str,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._quoter = quoter
        self._provider_company_id = provider_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        try:
            price_quote = await self._quoter.generate_quote(amqp_message.body.option_id)
        except cache.OptionNotFoundError:
            return

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=price_quote,
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )
