import datetime

import structlog

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.providers.save_a_train import (
    adapter as save_a_train_adapter,
)
from snowfall.project.junction.service.providers.save_a_train import cache
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import consumer, producer, types

_PROVIDER_NAME = "Save A Train"


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        price_cache: cache.PriceQuoteCache,
        price_ttl: datetime.timedelta,
    ):
        self._offer_cache = offer_cache
        self._price_cache = price_cache
        self._ttl = price_ttl
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._offer_cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=await self._price_cache.store(
                        cache.PriceQuote(
                            search_id=offer_details.search_id,
                            search_result_id=offer_details.search_result_id,
                            transfer_id=offer_details.transfer_id,
                            fare_id=offer_details.fare_id,
                        ),
                        expires_at=expires_at,
                    ),
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(expires_at),
                    price=money.from_string(
                        offer_details.price,
                        money.Currency(offer_details.currency),
                    ).protobuf(),
                ),
            ),
            routing_key="offers.result.price",
        )


class OrdersConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        offers_cache: cache.OffersCache,
        producer_obj: producer.Producer,
        adapter: save_a_train_adapter.SaveATrainAdapter,
    ):
        self._cache = offers_cache
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._adapter = adapter
        self._logger = structlog.get_logger(__name__)

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[orders_amqp_pb2.PlaceOrderTask],
    ) -> None:
        offer_details = await self._cache.fetch(message.body.booking.trip_option.id)
        message.body.booking.provider_name = _PROVIDER_NAME

        if not offer_details:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=message.body.booking.id,
                key=message.body.booking.trip_option.id,
            )

            return

        booking_result = await self._adapter.create_booking(
            task=message.body,
            offer_details=offer_details,
        )

        await self._producer.publish(
            booking_result,
            routing_key="orders.result.offer",
        )
