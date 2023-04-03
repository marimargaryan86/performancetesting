import structlog
from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.go.service.orders.v1alpha import (
    amqp_pb2 as orders_amqp_pb2,
)
from snowfall.project.junction.service.providers.ask2go import (
    booking,
    cache,
    pricing,
    transformer,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1alpha import seat_maps_pb2
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.models import seat_map

_PROVIDER_NAME = "Ask2Go"


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        pricing_adapter: pricing.Adapter,
        offer_transformer: transformer.OfferTransformer,
        offer_cache: cache.OfferCache,
        provider_company_id: str,
    ):
        self._pricing = pricing_adapter
        self._transformer = offer_transformer
        self._cache = offer_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj
        self._provider_company_id = provider_company_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=await self._transformer.to_price_quote(
                    price_result=await self._pricing.get_price_quote(
                        session_token=amqp_message.body.session_token,
                        offer_details=offer_details,
                    ),
                    option_id=amqp_message.body.option_id,
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )


class OrderConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        producer_obj: producer.Producer,
        booking_handler: booking.BookingHandler,
        price_quote_cache: cache.PriceQuoteCache,
    ):
        self._booking = booking_handler
        self._cache = price_quote_cache
        self._consumer = consumer_obj
        self._logger = structlog.get_logger(__name__)
        self._producer = producer_obj

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[orders_amqp_pb2.PlaceOrderTask],
    ) -> None:
        price_quote = await self._cache.fetch(
            amqp_message.body.booking.trip_option.price_quote_id,
        )
        amqp_message.body.booking.provider_name = _PROVIDER_NAME

        if not price_quote:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=amqp_message.body.booking.id,
                key=amqp_message.body.booking.trip_option.id,
            )

            return

        await self._producer.publish(
            await self._booking.book(task=amqp_message.body, quote=price_quote),
            routing_key="orders.result.offer",
        )


class SeatMapRpcServer(object):
    def __init__(  # noqa: WPS211
        self,
        address: str,
        exchange: amqp_types.Exchange,
        queue_name: str,
        routing_key: str,
        ask2go_client: client.Ask2GoClient,
        offer_cache: cache.OfferCache,
    ):
        self._address = address
        self._exchange = exchange
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._ask2go_client = ask2go_client
        self._cache = offer_cache

    async def consume(self) -> None:  # noqa: WPS217, WPS210
        # TODO: refactor to rpc_server class
        connection = await connect(self._address)
        channel = await connection.channel()

        queue = await channel.declare_queue(self._queue_name)

        consume_exchange = await channel.declare_exchange(
            name=self._exchange.name,
            type=self._exchange.type_,
            durable=True,
        )
        declared_exchange = channel.default_exchange

        await queue.bind(consume_exchange, self._routing_key)

        async with queue.iterator() as qiterator:
            message: AbstractIncomingMessage
            async for message in qiterator:
                async with message.process(requeue=False):
                    if message.reply_to is None:
                        continue  # noqa: WPS220
                    request = protobuf.AnySerializer[
                        seat_maps_pb2.GetSeatMapTask
                    ].deserialize(message.body)

                    offer_details = await self._cache.fetch(request.offer_option_id)

                    if not offer_details:
                        continue  # noqa: WPS220
                    response = seat_map.to_seat_map_pb(
                        await self._ask2go_client.get_seat_map(
                            search_id=offer_details.search_id,
                            itinerary_id=offer_details.itinerary_id,
                            brand_id=offer_details.brand_id,
                        ),
                    )
                    await declared_exchange.publish(
                        Message(
                            content_type="application/x-protobuf",
                            body=protobuf.AnySerializer.serialize(response),
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                    )
