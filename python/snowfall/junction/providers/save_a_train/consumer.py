from typing import cast

import phonenumbers

from snowfall.junction.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.junction.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.junction.orders.v1alpha import models_pb2
from snowfall.junction.providers.save_a_train import adapter as sat_adapter
from snowfall.junction.providers.save_a_train import cache, criteria
from snowfall.junction.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib.transport import amqp


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

    async def _process_message(self, message: amqp.Message) -> None:
        search = cast(offers_amqp_pb2.TripOfferSearchTask, message.body)

        for task in self._generator.from_search_task(search):
            await self._producer.publish(task, routing_key="offers.search.trip")


class SearchCriteriaConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        adapter: sat_adapter.SaveATrainAdapter,
    ):
        self._consumer = consumer
        self._producer = producer
        self._adapter = adapter

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        search = cast(amqp_pb2.SearchCriteriaTask, message.body)

        async for offer_result in self._adapter.gather_search_results(search):
            await self._producer.publish(offer_result, routing_key="offers.result.trip")


class OrdersConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        offers_cache: cache.OffersCache,
        producer: amqp.Producer,
        save_a_train_adapter: sat_adapter.SaveATrainAdapter,
    ):
        self._cache = offers_cache
        self._consumer = consumer
        self._producer = producer
        self._adapter = save_a_train_adapter

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        task = cast(orders_amqp_pb2.PlaceOrderTask, message.body)

        offer_details = await self._cache.fetch(task.offer_id)

        if not offer_details:
            return

        try:
            raw_data = await self._adapter.create_booking(
                task.order,
                offer_details,
            )
        except (phonenumbers.NumberParseException, sat_adapter.BookingError) as error:
            await self._producer.publish(
                models_pb2.OrderResult(
                    order_id=task.order.id,
                    offer_id=task.offer_id,
                    status=models_pb2.OrderResult.STATUS_ERROR,
                    raw_data=repr(error),
                ),
                routing_key="orders.result.offer",
            )
        else:
            await self._producer.publish(
                models_pb2.OrderResult(
                    order_id=task.order.id,
                    offer_id=task.offer_id,
                    status=models_pb2.OrderResult.STATUS_CONFIRMED,
                    raw_data=raw_data,
                ),
                routing_key="orders.result.offer",
            )
