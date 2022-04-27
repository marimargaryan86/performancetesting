from typing import cast

import phonenumbers

from snowfall.junction.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.junction.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.junction.orders.v1alpha import models_pb2
from snowfall.junction.providers.ask2go import adapter, booking, cache, criteria
from snowfall.junction.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib.transport import amqp
from snowfall.vendor.ask2go import errors


class OrderConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        booking_handler: booking.BookingHandler,
        offer_cache: cache.OfferCache,
    ):
        self._booking = booking_handler
        self._cache = offer_cache
        self._consumer = consumer
        self._producer = producer

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, amqp_message: amqp.Message) -> None:
        task = cast(orders_amqp_pb2.PlaceOrderTask, amqp_message.body)
        offer_details = await self._cache.fetch(task.offer_id)

        if not offer_details:
            return

        try:
            raw_data = await self._booking.book(
                task.order,
                task.offer_id,
                offer_details,
            )
        except (errors.ServiceError, phonenumbers.NumberParseException):
            await self._producer.publish(
                models_pb2.OrderResult(
                    order_id=task.order.id,
                    offer_id=task.offer_id,
                    status=models_pb2.OrderResult.STATUS_ERROR,
                    raw_data="",
                ),
                routing_key="orders.result.offer",
            )
        else:
            await self._producer.publish(
                models_pb2.OrderResult(
                    order_id=task.order.id,
                    offer_id=task.offer_id,
                    status=models_pb2.OrderResult.STATUS_NOT_TICKETED,
                    raw_data=raw_data.json(),
                ),
                routing_key="orders.result.offer",
            )


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        generator: criteria.CriteriaGenerator,
    ):
        self._consumer = consumer
        self._producer = producer
        self._generator = generator

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, amqp_message: amqp.Message) -> None:
        search = cast(offers_amqp_pb2.TripOfferSearchTask, amqp_message.body)

        for task in self._generator.from_search_task(search):
            await self._producer.publish(task, routing_key="offers.search.trip")


class SearchCriteriaConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        a2g_client: adapter.Ask2GoAdapter,
    ):
        self._consumer = consumer
        self._producer = producer
        self._client = a2g_client

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, amqp_message: amqp.Message) -> None:
        search = cast(amqp_pb2.SearchCriteriaTask, amqp_message.body)

        async for offer_result in self._client.gather_search_results(search):
            await self._producer.publish(offer_result, routing_key="offers.result.trip")
