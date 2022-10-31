import structlog

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
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

    async def _process_message(
        self,
        message: amqp.Message[offers_amqp_pb2.TripOfferSearchTask],
    ) -> None:
        for task in self._generator.from_search_task(message.body):
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

    async def _process_message(
        self,
        message: amqp.Message[amqp_pb2.SearchCriteriaTask],
    ) -> None:
        async for offer_result in self._adapter.gather_search_results(message.body):
            await self._producer.publish(
                offers_amqp_pb2.TripOfferSearchResult(
                    offer_search_id=message.body.offer_search_id,
                    offer=offer_result,
                ),
                routing_key="offers.result.trip",
            )


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

    async def _process_message(
        self,
        message: amqp.Message[orders_amqp_pb2.PlaceOrderTask],
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
