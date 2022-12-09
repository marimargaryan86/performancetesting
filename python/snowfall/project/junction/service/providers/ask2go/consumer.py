import structlog

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.providers.ask2go import (
    booking,
    cache,
    pricing,
    transformer,
)
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types

_PROVIDER_NAME = "Ask2Go"


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        pricing_adapter: pricing.Adapter,
        offer_transformer: transformer.OfferTransformer,
        offer_cache: cache.OfferCache,
    ):
        self._pricing = pricing_adapter
        self._transformer = offer_transformer
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=await self._transformer.to_price_quote(
                    price_result=await self._pricing.get_price_quote(
                        session_token=amqp_message.body.session_token,
                        offer_details=offer_details,
                    ),
                    option_id=amqp_message.body.option_id,
                ),
            ),
            routing_key="offers.result.price",
        )


class OrderConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        producer_obj: producer.Producer,
        booking_handler: booking.BookingHandler,
        price_quote_cache: cache.PriceQuoteCache,
    ):
        self._booking = booking_handler
        self._cache = price_quote_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[orders_amqp_pb2.PlaceOrderTask],
    ) -> None:
        price_quote = await self._cache.fetch(
            amqp_message.body.booking.trip_option.price_quote_id,
        )
        amqp_message.body.booking.provider_name = _PROVIDER_NAME

        if not price_quote:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=amqp_message.body.booking.id,
                key=amqp_message.body.booking.trip_option.id,
            )

            return

        await self._producer.publish(
            await self._booking.book(task=amqp_message.body, quote=price_quote),
            routing_key="orders.result.offer",
        )
