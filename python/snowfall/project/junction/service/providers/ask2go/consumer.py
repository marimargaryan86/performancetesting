from typing import cast

import phonenumbers
import structlog

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.orders.v1alpha import models_pb2
from snowfall.project.junction.service.providers.ask2go import (
    adapter,
    booking,
    cache,
    criteria,
    transformer,
)
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
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
        self._logger = structlog.get_logger(__name__)
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
            self._logger.exception()
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
        ask2go_adapter: adapter.Ask2GoAdapter,
        offer_transformer: transformer.OfferTransformer,
    ):
        self._consumer = consumer
        self._producer = producer
        self._adapter = ask2go_adapter
        self._transformer = offer_transformer

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, amqp_message: amqp.Message) -> None:
        search_task = cast(amqp_pb2.SearchCriteriaTask, amqp_message.body)

        with stdout.context_binding(
            origin=search_task.criteria.origin_iata,
            destination=search_task.criteria.destination_iata,
            departure_at=protobuf.protobuf_to_datetime(
                search_task.criteria.outbound_departure,
            ),
        ):
            offer_groups = self._transformer.offer_prices_to_offer_groups(
                search_task,
                self._adapter.gather_search_results(search_task),
            )

            async for offer_group in offer_groups:
                await self._producer.publish(
                    msg=offer_group,
                    routing_key="offers.result.trip",
                )
