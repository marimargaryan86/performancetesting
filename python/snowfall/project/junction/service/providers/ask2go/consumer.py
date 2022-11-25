import structlog

from snowfall.project.junction.provider import offers
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.providers.ask2go import (
    adapter,
    booking,
    cache,
    transformer,
)
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types

_PROVIDER_NAME = "Ask2Go"


class OrderConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        producer_obj: producer.Producer,
        booking_handler: booking.BookingHandler,
        offer_cache: cache.OfferCache,
    ):
        self._booking = booking_handler
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[orders_amqp_pb2.PlaceOrderTask],
    ) -> None:
        offer_details = await self._cache.fetch(
            amqp_message.body.booking.trip_option.id,
        )
        amqp_message.body.booking.provider_name = _PROVIDER_NAME

        if not offer_details:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=amqp_message.body.booking.id,
                key=amqp_message.body.booking.trip_option.id,
            )

            return

        await self._producer.publish(
            await self._booking.book(task=amqp_message.body, details=offer_details),
            routing_key="orders.result.offer",
        )


def _offer_group_cache_key(task: amqp_pb2.SearchCriteriaTask) -> str:
    return string.to_uuid(
        b"\x00".decode().join(
            [
                task.session_token,
                *[segment.id for segment in task.segments],
                task.criteria.cabin_class,
                str(task.criteria.adults),
                str(task.criteria.children),
                str(task.criteria.infants),
            ],
        ),
    )


class SearchCriteriaConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.SearchCriteriaTask],
        producer_obj: producer.Producer,
        ask2go_adapter: adapter.Ask2GoAdapter,
        offer_transformer: transformer.OfferTransformer,
        redis: types.Client[bytes],
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._adapter = ask2go_adapter
        self._transformer = offer_transformer
        self._redis = redis

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[amqp_pb2.SearchCriteriaTask],
    ) -> None:
        with stdout.context_binding(
            origin=amqp_message.body.criteria.origin_iata,
            destination=amqp_message.body.criteria.destination_iata,
            departure_at=protobuf.protobuf_to_datetime(
                amqp_message.body.criteria.outbound_departure,
            ).isoformat(),
        ):
            offer_cache = offers.OfferGroupCache(
                _offer_group_cache_key(amqp_message.body),
                self._redis,
            )

            async with offer_cache as has_lock:
                if has_lock:
                    await self._search_offers(amqp_message.body, offer_cache)
                else:
                    await amqp_message.nack(requeue=True)

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
            offer_groups = self._transformer.offer_prices_to_offer_groups(
                search_task,
                self._adapter.gather_search_results(search_task),
            )

            async for offer_group in offer_groups:
                await offer_cache.put(offer_group)
                await self._producer.publish(
                    msg=offers_amqp_pb2.TripOfferSearchResult(
                        offer_search_id=search_task.offer_search_id,
                        offer=offer_group,
                    ),
                    routing_key="offers.result.trip",
                )
