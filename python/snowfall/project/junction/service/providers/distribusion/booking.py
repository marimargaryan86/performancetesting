import asyncio
import datetime
import zoneinfo

from dateutil.relativedelta import relativedelta

from snowfall.project.junction.go.service.offers.v1alpha.models_pb2 import (
    OfferSegmentLeg,
)
from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.distribusion import (
    cache,
    notifications,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.vendor.distribusion import client, enums, errors
from snowfall.vendor.distribusion.models import criterias
from snowfall.vendor.distribusion.models import orders as model_orders


class BookingHandler(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 15

    def __init__(
        self,
        distribusion_client: client.DistribusionClient,
        notifier: notifications.Notifier,
        *,
        send_customer_email: bool = True,
    ):
        self._client = distribusion_client
        self._logger = stdout.get_logger()
        self._notifier = notifier
        self._send_customer_email = send_customer_email

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            booking_result = await self._make_booking(
                task=task,
                details=details,
                send_customer_email=self._send_customer_email,
            )
        except errors.ServiceError as error:
            self._logger.exception(
                "Booking failed",
                reason=repr(error),
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = repr(error)

            return new_booking

        if booking_result.booking is not None:
            booking_status = models_pb2.Booking.STATUS_NOT_TICKETED

            if booking_result.booking.marketing_carrier_booking_number:
                booking_status = models_pb2.Booking.STATUS_CONFIRMED

            new_booking.MergeFrom(
                models_pb2.Booking(
                    status=booking_status,
                    provider_total_price=money.Money(
                        amount=booking_result.booking.total_price or 0,
                        currency=money.Currency(booking_result.currency),
                    ).protobuf(),
                    trip_result=models_pb2.TripBooking(
                        provider_booking_reference=str(
                            booking_result.booking.identifier,
                        ),
                        record_locator=booking_result.booking.marketing_carrier_booking_number
                        or "",
                        operator_booking_references=(
                            [
                                booking_result.booking.distribusion_booking_number,
                            ]
                            if booking_result.booking.distribusion_booking_number
                            else []
                        ),
                        created_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.now(tz=datetime.UTC),
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
        *,
        send_customer_email: bool = True,
    ) -> model_orders.OrderResponse:
        first_trip_details = task.booking.trip_option.details[0]
        last_trip_details = task.booking.trip_option.details[-1]
        booker = task.passengers[0]
        first_segment = first_trip_details.segment.legs[0]
        last_segment = last_trip_details.segment.legs[-1]

        departure_time = (
            protobuf.protobuf_to_datetime(
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
            protobuf.protobuf_to_datetime(
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
            criterias.CreateOrder(
                marketing_carrier=first_trip_details.segment.vendor,
                departure_station=first_segment.origin.ref,
                arrival_station=last_segment.destination.ref,
                departure_time=departure_time,
                arrival_time=arrival_time,
                title=protobuf.enum_value_to_slug(
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
                total_price=details.price,
                currency=details.currency,
                locale="en",
                pax=len(task.passengers),
                terms_accepted=True,
                send_customer_email=send_customer_email,
                fare_class=details.fare_class,
                passengers=[
                    criterias.Passenger(
                        first_name=passenger.first_name,
                        last_name=passenger.last_name,
                        passenger_type=self._get_passenger_type(
                            first_segment,
                            details,
                            passenger,
                        ),
                    )
                    for passenger in task.passengers
                ],
            ),
        )

        order_response = await self._poll_booking(order_create_response)

        try:
            # TODO: this should be handled in a separate service
            await self._notifier.send(
                notifications.BookingNotification(task.metadata, order_response),
            )
        except notifications.NotificationError:
            self._logger.exception()

        return order_response

    async def _poll_booking(
        self,
        model: model_orders.OrderCreateResponse,
    ) -> model_orders.OrderResponse:
        for _ in range(self._poll_retries_limit):
            order = await self._client.get_order(model.identifier)

            if order.state == "executed":
                return order

            await asyncio.sleep(self._wait_time_between_polling)

        raise errors.ServiceError(
            "Unable to get order {0} details in time".format(model.identifier),
        )

    def _get_passenger_type(
        self,
        first_segment: OfferSegmentLeg,
        details: cache.OfferDetails,
        passenger: models_pb2.Passenger,
    ) -> str:
        departure_date = protobuf.protobuf_to_date(first_segment.departure_at)
        birth_date = protobuf.protobuf_to_date(passenger.date_of_birth)
        age = relativedelta(departure_date, birth_date)

        for pax_type in details.passenger_types:
            if pax_type.min_age <= age.years <= pax_type.max_age:
                return pax_type.type_code

        return "PNOS"
