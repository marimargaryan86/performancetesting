import phonenumbers
import structlog

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.duffel import cache, notifications
from snowfall.project.junction.service.providers.duffel.enums import gender_from_proto
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.vendor.duffel import client, errors
from snowfall.vendor.duffel.builders.order_request import (
    IdentityDocument,
    OrderBuilder,
    OrderPassenger,
    OrderPayment,
)
from snowfall.vendor.duffel.models.order import Order


class BookingHandler(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 15

    def __init__(
        self,
        duffel_client: client.DuffelClient,
        notifier: notifications.Notifier,
    ):
        self._client = duffel_client
        self._logger = structlog.get_logger(__name__)
        self._notifier = notifier

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            booking_result: Order = await self._make_booking(task=task, details=details)
        except errors.ServiceError:
            self._logger.exception()
            new_booking.status = models_pb2.Booking.STATUS_ERROR

            return new_booking

        if booking_result is not None:
            new_booking.MergeFrom(
                models_pb2.Booking(
                    status=models_pb2.Booking.STATUS_CONFIRMED,
                    total_price=money.from_string(
                        string_amount=str(
                            booking_result.total_amount,
                        ),
                        currency=money.Currency(
                            booking_result.total_currency,
                        ),
                    ).protobuf(),
                    trip_result=models_pb2.TripBooking(
                        provider_booking_reference=booking_result.identifier,
                        record_locator=booking_result.booking_reference or "",
                        created_at=protobuf.datetime_to_protobuf(
                            booking_result.created_at,
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

        for index, passenger in enumerate(task.passengers):
            document: IdentityDocument | None = None

            if passenger.doc_details:
                document = IdentityDocument(
                    unique_identifier=passenger.doc_details.document_number,
                    document_type="passport",
                    issuing_country_code=passenger.doc_details.issue_county,
                    expires_on=protobuf.protobuf_to_date(
                        passenger.doc_details.exp_date,
                    ),
                )

            order_request.add_passenger(
                OrderPassenger(
                    title=models_pb2.Passenger.Title.Name(passenger.title)[6:].lower(),
                    phone_number="+{country_code}{national_number}".format(
                        country_code=str(number.country_code),
                        national_number=str(number.national_number),
                    ),
                    passenger_id=details.passengers[index].identifier,
                    given_name=passenger.first_name,
                    gender=gender_from_proto(passenger.gender),
                    family_name=passenger.last_name,
                    email=task.contact_details.email,
                    born_on=protobuf.protobuf_to_date(passenger.date_of_birth),
                    identity_documents=[document]
                    if document and details.doc_required
                    else None,
                ),
            )

        order_response = await self._client.order_request(order_request.build())

        try:
            # todo: this should be handled in a separate service
            await self._notifier.send(
                notifications.BookingNotification(task.metadata, order_response),
            )
        except notifications.NotificationError:
            self._logger.exception()

        return order_response
