import asyncio
import datetime

import tenacity

from snowfall.project.junction.go.service.offers.v1 import (
    amqp_pb2 as offers_amqp_pb2,
)
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.service.orders.v1 import (
    amqp_pb2 as orders_amqp_pb2,
)
from snowfall.project.junction.provider import notifications as base_notifications
from snowfall.project.junction.service.providers.benerail import (
    booking,
    cache,
    helper_functions,
    notifications,
)
from snowfall.project.junction.service.providers.benerail.v1alpha import (
    amqp_pb2 as br_amqp_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models import etag
from snowfall.vendor.benerail.models.trip_offers import response

_PROVIDER_NAME = "Benerail"
_RETRY_TTL = datetime.timedelta(hours=1)
_RETRY_AFTER_SECONDS = 120


class NotificationsConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[br_amqp_pb2.BookingNotificationTask],
        benerail_client: client.BenerailClient,
        notifier: base_notifications.Notifier,
    ):
        self._consumer = consumer_obj
        self._client = benerail_client
        self._notifier = notifier
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(  # noqa: WPS217
        self,
        message: types.Message[br_amqp_pb2.BookingNotificationTask],
    ) -> None:
        body = message.body
        etag_data = etag.EtagData()

        try:
            booking_res, _ = await self._client.bookings_client.get_booking(
                booking_id=body.br_booking_id,
                session_token=body.br_session_token,
            )
        except errors.HttpError:
            self._logger.exception("Failed to fetch the booking")

            return await self._handle_no_fulfillment(message)

        booking_res.set_etags(etag_data)

        if not booking_res.response_result.fulfillments:
            return await self._handle_no_fulfillment(message)

        ticket_urls = (
            await self._client.bookings_client.get_ticket_urls_from_fulfillment(
                booking_id=booking_res.response_result.identifier,
                fulfillment_id=helper_functions.last_id_of_url(
                    booking_res.response_result.fulfillments[0].href,
                ),
            )
        )

        if not ticket_urls:
            return await self._handle_no_fulfillment(message)

        body.MergeFrom(
            br_amqp_pb2.BookingNotificationTask(
                ticket_url=", ".join(ticket_urls),
            ),
        )

        await self._notifier.send(
            notifications.BookingNotification(body),
        )
        return None

    async def _handle_no_fulfillment(
        self,
        message: types.Message[br_amqp_pb2.BookingNotificationTask],
    ) -> None:
        await asyncio.sleep(_RETRY_AFTER_SECONDS)

        created_at = protobuf.protobuf_to_datetime(
            message.body.created_at,
        )
        time_passed = datetime.datetime.now(datetime.UTC) - created_at

        if time_passed > _RETRY_TTL:
            self._logger.error(
                "Ticket retrieval limit reached",
                booking_id=message.body.booking_id,
            )
            await message.nack()
        else:
            await message.requeue()


class PriceQuoteConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[offers_amqp_pb2.TripPriceQuoteTask],
        producer_obj: producer.Producer,
        offer_cache: cache.OffersCache,
        benerail_client: client.BenerailClient,
        price_ttl: datetime.timedelta,
        provider_company_id: str,
    ):
        self._offer_cache = offer_cache
        self._ttl = price_ttl
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._benerail_client = benerail_client
        self._provider_company_id = provider_company_id
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(errors.HttpError),
        wait=tenacity.wait_fixed(3),
        reraise=True,
    )
    async def _get_offer_info(
        self,
        offer_id: str,
        session_token: str | None = None,
    ) -> response.GetOfferResponse:
        return await self._benerail_client.offers_client.get_offer_info(
            offer_id=offer_id,
            session_token=session_token,
        )

    async def _process_message(
        self,
        amqp_message: types.Message[offers_amqp_pb2.TripPriceQuoteTask],
    ) -> None:
        offer_details = await self._offer_cache.fetch(amqp_message.body.option_id)

        if not offer_details:
            return

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl
        price_quote_id = await self._offer_cache.store(offer_details, expires_at)

        try:
            offer_info = await self._get_offer_info(
                offer_id=offer_details.offer_id,
                session_token=offer_details.session_token,
            )
        except errors.HttpError:
            self._logger.exception(
                "Failed to get offer for quotation",
                offer_id=offer_details.offer_id,
                br_session_token=offer_details.session_token,
            )

            return

        price_quote_price_proto = money.from_string(
            str(offer_info.response_result.price.amount),
            money.Currency(
                offer_info.response_result.price.currency.upper(),
            ),
        ).protobuf()

        await self._producer.publish(
            offers_amqp_pb2.TripPriceQuoteResult(
                price_quote_container_id=amqp_message.body.price_quote_container_id,
                option_id=amqp_message.body.option_id,
                price_quote=offers_pb2.PriceQuote(
                    id=price_quote_id,
                    option_id=amqp_message.body.option_id,
                    expires_at=protobuf.datetime_to_protobuf(expires_at),
                    price=price_quote_price_proto,
                    price_breakdown=[
                        offers_pb2.PriceBreakdown(
                            price=price_quote_price_proto,
                            breakdown_type=offers_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                        ),
                    ],
                    required_documents=[],
                    rules=[],
                ),
                provider_company_id=self._provider_company_id,
            ),
            routing_key="offers.result.price",
        )


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

        try:
            booking_result = await self._bookings.create_booking(
                task=message.body,
                offer_details=offer_details,
            )
        except errors.HttpError:
            self._logger.exception(
                "Failed to create booking",
                br_session_token=offer_details.session_token,
                br_offer_id=offer_details.offer_id,
                booking_id=message.body.booking.id,
            )

            return

        await self._producer.publish(
            booking_result,
            routing_key="orders.result.offer",
        )
