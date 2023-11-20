import asyncio
import base64
import datetime
import pathlib

import orjson

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.service.orders.v1 import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.service.providers.save_a_train import (
    adapter as save_a_train_adapter,
)
from snowfall.project.junction.service.providers.save_a_train import (
    cache,
    notifications,
)
from snowfall.project.junction.service.providers.save_a_train.v1 import (
    amqp_pb2 as sat_amqp_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer, types

_PROVIDER_NAME = "Save A Train"
_RETRY_TTL = datetime.timedelta(hours=1)
_RETRY_AFTER_SECONDS = 120


class NotificationsConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[sat_amqp_pb2.BookingNotificationTask],
        adapter: save_a_train_adapter.SaveATrainAdapter,
        notifier: base_notifications.Notifier,
        booking_storage: filesystem.Storage,
    ):
        self._booking_storage = booking_storage
        self._consumer = consumer_obj
        self._adapter = adapter
        self._notifier = notifier
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[sat_amqp_pb2.BookingNotificationTask],
    ) -> None:
        if not message.body.ticket_url:
            get_ticket_result, _ = await self._adapter.get_ticket(
                search_id=message.body.search_identifier,
            )

            if not get_ticket_result.url:
                return await self._handle_no_fulfillment(message)

            message.body.ticket_url = get_ticket_result.url

        storage_path = pathlib.Path(message.body.search_identifier)
        raw_data = await self._booking_storage.get(storage_path)
        combined = orjson.loads(raw_data)
        combined["ticket_urls"] = base64.b64encode(
            orjson.dumps([message.body.ticket_url]),
        ).decode()

        await asyncio.gather(
            self._booking_storage.put(storage_path, orjson.dumps(combined)),
            self._notifier.send(
                notifications.BookingNotification(message.body),
            ),
        )

        return None

    async def _handle_no_fulfillment(
        self,
        message: types.Message[sat_amqp_pb2.BookingNotificationTask],
    ) -> None:
        await asyncio.sleep(_RETRY_AFTER_SECONDS)

        created_at = protobuf.protobuf_to_datetime(
            message.body.created_at,
        )
        time_passed = datetime.datetime.now(datetime.UTC) - created_at

        if time_passed > _RETRY_TTL:
            self._logger.error(
                "Ticket retrieval limit reached",
                booking_id=message.body.booking_id,
            )
            await message.nack()
        else:
            await message.requeue()


class PriceQuoteConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        price_quote_cache: cache.PriceQuoteCache,
        price_ttl: datetime.timedelta,
        provider_company_id: str,
    ):
        self._offer_cache = offer_cache
        self._price_quote_cache = price_quote_cache
        self._ttl = price_ttl
        self._consumer = consumer_obj
        self._logger = stdout.get_logger()
        self._producer = producer_obj
        self._provider_company_id = provider_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._offer_cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl

        price_quote = cache.PriceQuote(
            search_id=offer_details.search_id,
            search_result_id=offer_details.search_result_id,
            transfer_id=offer_details.transfer_id,
            fare_id=offer_details.fare_id,
        )

        price_quote_id = await self._price_quote_cache.store(price_quote, expires_at)

        price_quote_price = money.from_string(
            offer_details.price,
            money.Currency(offer_details.currency),
        ).protobuf()

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=price_quote_id,
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(expires_at),
                    price=price_quote_price,
                    price_breakdown=[
                        offers_pb2.PriceBreakdown(
                            price=price_quote_price,
                            breakdown_type=offers_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )


class OrdersConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        price_quote_cache: cache.PriceQuoteCache,
        producer_obj: producer.Producer,
        adapter: save_a_train_adapter.SaveATrainAdapter,
        provider_id: str,
    ):
        self._price_quote_cache = price_quote_cache
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._adapter = adapter
        self._logger = stdout.get_logger()
        self._provider_id = provider_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[orders_amqp_pb2.PlaceOrderTask],
    ) -> None:
        price_quote = await self._price_quote_cache.fetch(
            message.body.booking.trip_option.price_quote_id,
        )
        message.body.booking.provider_name = _PROVIDER_NAME
        message.body.booking.provider_id = self._provider_id

        if not price_quote:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=message.body.booking.id,
                key=message.body.booking.trip_option.id,
            )
            return

        booking_result = await self._adapter.create_booking(
            task=message.body,
            price_quote=price_quote,
        )

        await self._producer.publish(
            booking_result,
            routing_key="orders.result.offer",
        )
