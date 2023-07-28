import datetime

from snowfall.project.junction.go.service.offers.v1 import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.service.orders.v1 import amqp_pb2 as orders_amqp_pb2
from snowfall.project.junction.service.providers.direct_ferries import (
    booking,
    cache,
    route,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.v1 import amqp_pb2 as trackable_pb2

_PROVIDER_NAME = "Direct Ferries"
_INFO_ATTR_REQUIREMENT_MAP = (
    ("need_passport", offers_pb2.PriceQuote.REQUIRED_PASSPORT_NUMBER),
    ("need_date_of_birth", offers_pb2.PriceQuote.REQUIRED_DATE_OF_BIRTH),
    ("need_nationality", offers_pb2.PriceQuote.REQUIRED_NATIONALITY),
    ("need_passport_expiry_date", offers_pb2.PriceQuote.REQUIRED_EXPIRATION_DATE),
    ("need_passport_start_date", offers_pb2.PriceQuote.REQUIRED_ISSUE_DATE),
)
TripSearchMessages = offers_amqp_pb2.TripOfferSearchTask | trackable_pb2.Trackable


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        price_ttl: datetime.timedelta,
        provider_company_id: str,
        routes: route.RouteRepository,
    ):
        self._offer_cache = offer_cache
        self._ttl = price_ttl
        self._consumer = consumer_obj
        self._logger = stdout.get_logger()
        self._producer = producer_obj
        self._provider_company_id = provider_company_id
        self._routes = routes

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

        rules = []

        if offer_details.quote.ticket_conditions:
            rules.append(
                offers_pb2.FareRule(
                    title="Ticket conditions",
                    body=offer_details.quote.ticket_conditions,
                ),
            )

        price_quote_price = money.from_string(
            str(offer_details.quote.price.total_in_selected_currency),
            money.Currency(offer_details.quote.selected_currency),
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
                    required_documents=list(
                        {
                            req
                            for leg in offer_details.quote.legs
                            for req in self._get_required_docs(leg.route_id)
                        },
                    ),
                    rules=rules,
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )

    def _get_required_docs(
        self,
        route_id: int,
    ) -> list[offers_pb2.PriceQuote.Required.ValueType]:
        route_obj = self._routes.get_by_id(route_id)
        passenger_info = route_obj.passenger_info

        if not passenger_info:
            return []

        return [
            doc_requirement
            for pax_info_attr_name, doc_requirement in _INFO_ATTR_REQUIREMENT_MAP
            if getattr(passenger_info, pax_info_attr_name)
        ]


class OrdersConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[orders_amqp_pb2.PlaceOrderTask],
        offers_cache: cache.OffersCache,
        producer_obj: producer.Producer,
        bookings: booking.BookingHandler,
    ):
        self._cache = offers_cache
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._bookings = bookings
        self._logger = stdout.get_logger()

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

        if not offer_details:
            self._logger.warning(
                "No offer details found for booking",
                booking_id=message.body.booking.id,
                key=message.body.booking.trip_option.id,
            )

            return

        booking_result = await self._bookings.create_booking(
            task=message.body,
            offer_details=offer_details,
        )

        await self._producer.publish(
            booking_result,
            routing_key="orders.result.offer",
        )
