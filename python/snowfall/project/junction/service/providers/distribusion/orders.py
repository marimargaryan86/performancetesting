import asyncio
import contextlib
import datetime
import random
import zoneinfo
from typing import Sequence

import aiosmtplib
import httpx
import pydantic
import structlog
from redis import asyncio as aioredis

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.distribusion import (
    cache,
    config,
    notifications,
)
from snowfall.stdlib import format, money, persistence, service, transport
from snowfall.vendor.distribusion import client, enums, errors, models

_PROVIDER_NAME = "Distribusion"


class OrdersSettings(config.DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    smtp_sender: pydantic.EmailStr
    smtp_recipient: pydantic.EmailStr


async def orders(app: service.Application[OrdersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
            ),
        )
        redis_connection = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )
        amqp_connection = await stack.enter_async_context(
            transport.amqp.types.Connection(app.settings.amqp_dsn),
        )
        distribusion_client = client.DistribusionClient(
            api_base_url=app.settings.api_base_url,
            api_key=app.settings.api_key,
            retailer_partner_number=app.settings.retailer_partner_number,
            http_client=http_client,
        )

        await OrderConsumer(
            consumer_obj=transport.amqp.consumer.Consumer(
                connection=amqp_connection,
                queue_name="{0}_orders".format(app.name),
                binds=[(transport.amqp.types.Exchange("orders"), "orders.offers")],
            ),
            producer_obj=transport.amqp.producer.Producer(
                connection=amqp_connection,
                exchange=transport.amqp.types.Exchange("orders"),
            ),
            booking_handler=BookingHandler(
                distribusion_client=distribusion_client,
                notifier=notifications.SmtpNotifier(
                    smtp_client=aiosmtplib.SMTP(
                        hostname=app.settings.smtp_dsn.host,
                        port=int(app.settings.smtp_dsn.port or 0) or None,
                        username=app.settings.smtp_dsn.user,
                        password=app.settings.smtp_dsn.password,
                        start_tls=True,
                    ),
                    sender=app.settings.smtp_sender,
                    recipient=app.settings.smtp_recipient,
                ),
            ),
            offer_cache=cache.OffersCache(
                client=persistence.redis.types.Client[bytes](
                    redis_connection,
                    prefix=app.name,
                ),
            ),
        ).consume()


class BookingHandler(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 15

    def __init__(
        self,
        distribusion_client: client.DistribusionClient,
        notifier: notifications.Notifier,
    ):
        self._client = distribusion_client
        self._logger = structlog.get_logger(__name__)
        self._notifier = notifier

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            booking_result = await self._make_booking(task=task, details=details)
        except errors.ServiceError:
            self._logger.exception()
            new_booking.status = models_pb2.Booking.STATUS_ERROR

            return new_booking

        if booking_result.booking is not None:
            new_booking.MergeFrom(
                models_pb2.Booking(
                    status=models_pb2.Booking.STATUS_NOT_TICKETED,
                    total_price=money.from_string(
                        string_amount=str(
                            booking_result.booking.total_price,
                        ),
                        currency=money.Currency(
                            booking_result.currency,
                        ),
                    ).protobuf(),
                    trip_result=models_pb2.TripBooking(
                        provider_booking_reference=str(
                            booking_result.booking.identifier,
                        ),
                        record_locator=booking_result.booking.marketing_carrier_booking_number
                        or "",
                        operator_booking_references=booking_result.booking.distribusion_booking_number
                        or [],
                        created_at=format.protobuf.datetime_to_protobuf(
                            datetime.datetime.now(tz=datetime.timezone.utc),
                        ),
                    ),
                    raw_data=booking_result.json(),
                ),
            )

        return new_booking

    async def _make_booking(  # noqa: WPS210
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> models.orders.OrderResponse:
        first_trip_details = task.booking.trip_option.details[0]
        last_trip_details = task.booking.trip_option.details[-1]
        booker = task.passengers[0]
        first_segment = first_trip_details.segment.legs[0]
        last_segment = last_trip_details.segment.legs[-1]

        departure_time = (
            format.protobuf.protobuf_to_datetime(
                first_segment.departure_at,
            )
            .astimezone(  # noqa: WPS348
                zoneinfo.ZoneInfo(first_segment.origin.time_zone),
            )
            .replace(  # noqa: WPS348
                tzinfo=None,
            )
            .isoformat(  # noqa: WPS348
                timespec="minutes",
            )
        )

        arrival_time = (
            format.protobuf.protobuf_to_datetime(
                last_segment.arrival_at,
            )
            .astimezone(  # noqa: WPS348
                zoneinfo.ZoneInfo(last_segment.destination.time_zone),
            )
            .replace(  # noqa: WPS348
                tzinfo=None,
            )
            .isoformat(  # noqa: WPS348
                timespec="minutes",
            )
        )

        order_create_response = await self._client.create_order(
            models.criterias.CreateOrder(
                marketing_carrier=first_trip_details.segment.vendor,
                departure_station=first_segment.origin.ref,
                arrival_station=last_segment.destination.ref,
                departure_time=departure_time,
                arrival_time=arrival_time,
                title=format.protobuf.enum_value_to_slug(
                    enum_descriptor=models_pb2.Passenger.Title.DESCRIPTOR,
                    enum_value=booker.title,
                ).lower(),
                first_name=booker.first_name,
                last_name=booker.last_name,
                email=task.contact_details.email,
                phone=task.contact_details.phone.e164_number.replace("+", ""),
                city=task.contact_details.address.locality,
                zip_code=task.contact_details.address.postal_code,
                street_and_number="\n".join(task.contact_details.address.address_lines),
                execute_payment=True,
                payment_method=enums.PaymentMethod.demand_note,
                total_price=money.from_protobuf(task.booking.trip_option.price).amount,
                currency=task.booking.trip_option.price.currency_code,
                locale="en",
                pax=len(task.passengers),
                terms_accepted=True,
                send_customer_email=False,
                fare_class=details.fare_class,
                passengers=[
                    models.criterias.Passenger(
                        first_name=passenger.first_name,
                        last_name=passenger.last_name,
                        passenger_type="PNOS",  # TODO get this properly
                    )
                    for passenger in task.passengers
                ],
            ),
        )

        order_response = await self._poll_booking(order_create_response)

        try:
            # todo: this should be handled in a separate service
            await self._notifier.send(
                notifications.BookingNotification(task.metadata, order_response),
            )
        except notifications.NotificationError:
            self._logger.exception()

        return order_response

    async def _poll_booking(
        self,
        model: models.orders.OrderCreateResponse,
    ) -> models.orders.OrderResponse:
        for _ in range(self._poll_retries_limit):
            order = await self._client.get_order(model.identifier)

            if order.state == "executed":
                return order

            await asyncio.sleep(self._wait_time_between_polling)

        raise errors.ServiceError(
            "Unable to get order {0} details in time".format(model.identifier),
        )


class OrderConsumer(object):
    def __init__(
        self,
        consumer_obj: transport.amqp.consumer.Consumer[amqp_pb2.PlaceOrderTask],
        producer_obj: transport.amqp.producer.Producer,
        booking_handler: BookingHandler,
        offer_cache: cache.OffersCache,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._booking = booking_handler
        self._cache = offer_cache
        self._logger = structlog.get_logger(__name__)

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: transport.amqp.types.Message[amqp_pb2.PlaceOrderTask],
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
