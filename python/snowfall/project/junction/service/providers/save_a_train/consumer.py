from typing import cast

import structlog

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import models_pb2
from snowfall.project.junction.service.providers.save_a_train import (
    adapter as save_a_train_adapter,
)
from snowfall.project.junction.service.providers.save_a_train import cache, criteria
from snowfall.project.junction.service.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib.transport import amqp

_PROVIDER_NAME = "Save A Train"


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
        adapter: save_a_train_adapter.SaveATrainAdapter,
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
        adapter: save_a_train_adapter.SaveATrainAdapter,
    ):
        self._cache = offers_cache
        self._consumer = consumer
        self._producer = producer
        self._adapter = adapter
        self._logger = structlog.get_logger(__name__)

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        task = cast(orders_amqp_pb2.PlaceOrderTask, message.body)
        offer_details = await self._cache.fetch(task.booking.trip_option.id)
        task.booking.provider_name = _PROVIDER_NAME

        if not offer_details:
            self._logger.error(
                "No offer details found for booking",
                booking_id=task.booking.id,
                key=task.booking.trip_option.id,
            )
            task.booking.status = models_pb2.Booking.STATUS_ERROR

            await self._producer.publish(
                task.booking,
                routing_key="orders.result.offer",
            )

            return

        booking_result = await self._adapter.create_booking(
            task=task,
            offer_details=offer_details,
        )

        await self._producer.publish(
            booking_result,
            routing_key="orders.result.offer",
        )
