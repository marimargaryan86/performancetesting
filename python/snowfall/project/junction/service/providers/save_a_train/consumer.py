import structlog

from snowfall.project.junction.provider import offers
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.providers.save_a_train import (
    adapter as save_a_train_adapter,
)
from snowfall.project.junction.service.providers.save_a_train import cache
from snowfall.project.junction.service.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.transport.amqp import consumer, producer, types

_PROVIDER_NAME = "Save A Train"


def _offer_group_cache_key(task: amqp_pb2.SearchCriteriaTask) -> str:
    return string.to_uuid(
        b"\x00".decode().join(
            [
                task.session_token,
                *[segment.id for segment in task.segments],
                task.criteria.cabin_class,
                *[str(age) for age in task.criteria.passengers_ages],
            ],
        ),
    )


class SearchCriteriaConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.SearchCriteriaTask],
        producer_obj: producer.Producer,
        adapter: save_a_train_adapter.SaveATrainAdapter,
        redis: redis_types.Client[bytes],
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._adapter = adapter
        self._redis = redis

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.SearchCriteriaTask],
    ) -> None:
        offer_cache = offers.OfferGroupCache(
            _offer_group_cache_key(message.body),
            self._redis,
        )

        async with offer_cache as has_lock:
            if has_lock:
                await self._search_offers(message.body, offer_cache)
            else:
                await message.nack(requeue=True)

    async def _search_offers(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        offer_cache: offers.OfferGroupCache,
    ) -> None:
        try:
            async for cached_offer_group in offer_cache.to_iterable():
                await self._producer.publish(
                    msg=offers_amqp_pb2.TripOfferSearchResult(
                        offer_search_id=search_task.offer_search_id,
                        offer=cached_offer_group,
                    ),
                    routing_key="offers.result.trip",
                )
        except offers.NoCacheExistsError:
            async for offer_result in self._adapter.gather_search_results(search_task):
                await offer_cache.put(offer_result)
                await self._producer.publish(
                    msg=offers_amqp_pb2.TripOfferSearchResult(
                        offer_search_id=search_task.offer_search_id,
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
