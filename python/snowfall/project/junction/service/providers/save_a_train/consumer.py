import datetime

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
from snowfall.stdlib.transport.amqp import consumer, producer, types

_PROVIDER_NAME = "Save A Train"


class NotificationsConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[sat_amqp_pb2.BookingNotificationTask],
        adapter: save_a_train_adapter.SaveATrainAdapter,
        notifier: base_notifications.Notifier,
    ):
        self._consumer = consumer_obj
        self._adapter = adapter
        self._notifier = notifier

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[sat_amqp_pb2.BookingNotificationTask],
    ) -> None:
        if message.body.ticket_url:
            await self._notifier.send(
                notifications.BookingNotification(message.body),
            )
            return

        get_ticket_result, raw_ticket = await self._adapter.get_ticket(
            search_id=message.body.search_identifier,
        )
        if get_ticket_result.url:
            message.body.ticket_url = get_ticket_result.url
            await self._notifier.send(
                notifications.BookingNotification(message.body),
            )
        else:
            await message.nack()


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        price_cache: cache.PriceQuoteCache,
        price_ttl: datetime.timedelta,
        provider_company_id: str,
    ):
        self._offer_cache = offer_cache
        self._price_cache = price_cache
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

        price_quote_id = await self._offer_cache.store(offer_details, expires_at)

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
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        offers_cache: cache.OffersCache,
        producer_obj: producer.Producer,
        adapter: save_a_train_adapter.SaveATrainAdapter,
        provider_id: str,
    ):
        self._cache = offers_cache
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
        offer_details = await self._cache.fetch(
            message.body.booking.trip_option.price_quote_id,
        )
        message.body.booking.provider_name = _PROVIDER_NAME
        message.body.booking.provider_id = self._provider_id

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
