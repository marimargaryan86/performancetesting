import phonenumbers
import structlog
from dateutil.relativedelta import relativedelta

from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.duffel import cache, notifications
from snowfall.project.junction.service.providers.duffel.enums import gender_from_proto
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import date_pb2
from snowfall.vendor.duffel import client, errors
from snowfall.vendor.duffel.builders.order_request import (
    IdentityDocument,
    OrderBuilder,
    OrderPassenger,
    OrderPayment,
)
from snowfall.vendor.duffel.models.order import Order


class BookingHandler(object):  # noqa: WPS214
    _poll_retries_limit = 10
    _wait_time_between_polling = 15
    _adult_years = 18
    _infant_years = 2

    def __init__(
        self,
        duffel_client: client.DuffelClient,
        notifier: notifications.Notifier,
        price_change_tolerance_percent: float,
    ):
        self._client = duffel_client
        self._logger = structlog.get_logger(__name__)
        self._notifier = notifier
        self._price_change_tolerance_percent = price_change_tolerance_percent

    async def book(  # noqa: C901, WPS210
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            updated_details: cache.OfferDetails = await self._refresh_details(details)
        except errors.ServiceError as offer_refresh_error:
            self._logger.exception(
                "Booking failed",
                reason=repr(offer_refresh_error),
            )
            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = repr(offer_refresh_error)
            return new_booking

        original_price = float(details.total_amount)
        updated_price = float(updated_details.total_amount)
        price_difference_percent = (
            (updated_price - original_price) * 100 / original_price
        )

        if details.total_amount != updated_details.total_amount:
            self._logger.warning(
                "Price changed",
                old_price=details.total_amount,
                new_price=updated_details.total_amount,
                offer_id=details.offer_id,
            )

        if abs(price_difference_percent) > self._price_change_tolerance_percent:
            error_text = (
                "Offer price changed from {original_price} to {updated_price}."
                "Price change exceeded {price_change_tolerance}%"
            ).format(
                updated_price=updated_price,
                original_price=original_price,
                price_change_tolerance=self._price_change_tolerance_percent,
            )
            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = repr(errors.ServiceError(error_text))
            return new_booking

        try:
            booking_result: Order = await self._make_booking(
                task=task,
                details=updated_details,
            )
        except errors.ServiceError as booking_error:
            self._logger.exception(
                "Booking failed",
                reason=repr(booking_error),
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = repr(booking_error)
            return new_booking

        if booking_result is not None:
            new_booking.MergeFrom(
                models_pb2.Booking(
                    status=models_pb2.Booking.STATUS_CONFIRMED,
                    provider_total_price=money.from_string(
                        string_amount=(
                            booking_result.total_amount
                            if price_difference_percent <= 0
                            else details.total_amount
                        ),
                        currency=money.Currency(
                            booking_result.total_currency,
                        ),
                    ).protobuf(),
                    trip_result=models_pb2.TripBooking(
                        provider_booking_reference=booking_result.identifier,
                        record_locator=booking_result.booking_reference or "",
                        operator_booking_references=(
                            [booking_result.booking_reference]
                            if booking_result.booking_reference
                            else []
                        ),
                        created_at=protobuf.datetime_to_protobuf(
                            booking_result.created_at,
                        ),
                    ),
                    raw_data=booking_result.json(),
                ),
            )

        return new_booking

    async def _refresh_details(
        self,
        details: cache.OfferDetails,
    ) -> cache.OfferDetails:
        try:
            offer = await self._client.get_single_offer(details.offer_id)
        except errors.ServiceError as get_offer_ex:
            self._logger.error(
                "Could not get offer from Duffel",
                exception=str(type(get_offer_ex).__name__),
            )
            raise

        return cache.OfferDetails(
            offer_id=details.offer_id,
            passengers=details.passengers,
            total_amount=offer.total_amount,
            currency=offer.total_currency,
            doc_required=details.doc_required,
            last_travel_date=details.last_travel_date,
        )

    async def _make_booking(  # noqa: WPS210, WPS231
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> Order:
        number = phonenumbers.parse(task.contact_details.phone.e164_number)
        order_request = OrderBuilder()
        order_request.add_offer_id(details.offer_id)
        order_request.add_payment(
            OrderPayment(
                payment_type="balance",
                currency=details.currency,
                amount=details.total_amount,
            ),
        )

        sorted_passengers = sorted(
            details.passengers,
            key=lambda passenger_type: passenger_type.passenger_type or "adult",
        )

        infant_id_list = [
            sorted_passengers[index].identifier
            for index, passenger in enumerate(task.passengers)
            if self._is_infant(passenger, details)
        ]

        for index, passenger in enumerate(task.passengers):
            document: IdentityDocument | None = None

            if details.doc_required and self._has_valid_document(passenger):
                document = IdentityDocument(
                    unique_identifier=passenger.doc_details.document_number,
                    document_type="passport",
                    issuing_country_code=passenger.doc_details.issue_county,
                    expires_on=protobuf.protobuf_to_date(
                        passenger.doc_details.exp_date,
                    ),
                )

            order_passenger = OrderPassenger(
                title=models_pb2.Passenger.Title.Name(passenger.title)[6:].lower(),
                phone_number="+{country_code}{national_number}".format(
                    country_code=str(number.country_code),
                    national_number=str(number.national_number),
                ),
                passenger_id=sorted_passengers[index].identifier,
                given_name=passenger.first_name,
                gender=gender_from_proto(passenger.gender),
                family_name=passenger.last_name,
                email=task.contact_details.email,
                born_on=protobuf.protobuf_to_date(passenger.date_of_birth),
                identity_documents=[document] if document is not None else None,
            )

            if infant_id_list and self._is_adult(passenger, details):
                order_passenger.infant_passenger_id = infant_id_list.pop(0)

            order_request.add_passenger(order_passenger)

        order_response = await self._client.order_request(order_request.build())

        try:
            # TODO: this should be handled in a separate service
            await self._notifier.send(
                notifications.BookingNotification(task.metadata, order_response),
            )
        except notifications.NotificationError:
            self._logger.exception()

        return order_response

    def _is_infant(
        self,
        passenger: models_pb2.Passenger,
        details: cache.OfferDetails,
    ) -> bool:
        return (
            relativedelta(
                details.last_travel_date,
                protobuf.protobuf_to_date(passenger.date_of_birth),
            ).years
            < self._infant_years
        )

    def _is_adult(
        self,
        passenger: models_pb2.Passenger,
        details: cache.OfferDetails,
    ) -> bool:
        return (
            relativedelta(
                details.last_travel_date,
                protobuf.protobuf_to_date(passenger.date_of_birth),
            ).years
            >= self._adult_years
        )

    def _has_valid_document(self, passenger: models_pb2.Passenger) -> bool:
        if passenger.doc_details.document_number == "":
            return False

        return self._is_valid_date(passenger.doc_details.exp_date)

    def _is_valid_date(self, date: date_pb2.Date) -> bool:
        return date.year > 0 and date.month > 0 and date.day > 0
