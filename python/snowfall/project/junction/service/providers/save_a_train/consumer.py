import structlog

from snowfall.project.junction.provider import status
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.providers.save_a_train import (
    adapter as save_a_train_adapter,
)
from snowfall.project.junction.service.providers.save_a_train import cache, criteria
from snowfall.project.junction.service.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib.transport.amqp import consumer, producer, trackable, types
from snowfall.stdlib.v1alpha import amqp_pb2 as trackable_pb2

_PROVIDER_NAME = "Save A Train"
TripSearchMessages = offers_amqp_pb2.TripOfferSearchTask | trackable_pb2.Trackable


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[TripSearchMessages],
        producer_obj: trackable.TrackableProducer,
        generator: criteria.CriteriaGenerator,
        status_handler: status.SubtaskStatusHandler,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._generator = generator
        self._status_handler = status_handler

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[TripSearchMessages],
    ) -> None:
        match message.body:
            case offers_amqp_pb2.TripOfferSearchTask():
                await self._process_trip_offer_search_task(message.body)
            case trackable_pb2.Trackable():
                await self._status_handler.on_message(message.body)

    async def _process_trip_offer_search_task(
        self,
        body: offers_amqp_pb2.TripOfferSearchTask,
    ) -> None:
        tasks = list(self._generator.from_search_task(body))

        await self._status_handler.set_expected_size(
            body.offer_search_id,
            len(tasks),
        )

        for task in tasks:
            await self._producer.publish(
                task,
                routing_key="offers.search.trip",
                trackable_id=body.offer_search_id,
            )


class SearchCriteriaConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.SearchCriteriaTask],
        producer_obj: producer.Producer,
        adapter: save_a_train_adapter.SaveATrainAdapter,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._adapter = adapter

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.SearchCriteriaTask],
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
