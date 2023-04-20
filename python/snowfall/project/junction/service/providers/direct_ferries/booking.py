import datetime

import phonenumbers

from snowfall.project.junction.go.service.orders.v1alpha import (
    amqp_pb2 as order_amqp_pb2,
)
from snowfall.project.junction.go.service.orders.v1alpha import models_pb2
from snowfall.project.junction.go.service.orders.v1alpha import (
    models_pb2 as order_models_pb2,
)
from snowfall.project.junction.service.providers.direct_ferries import cache
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.models import passenger, quote


class PassengerCountNotMatchingError(Exception):
    """Raised when the number of passengers changed during the booking."""


class BookingHandler(object):
    def __init__(self, df_client: client.DfHttpClient) -> None:
        self._client = df_client

    async def create_booking(
        self,
        task: order_amqp_pb2.PlaceOrderTask,
        offer_details: cache.OfferDetails,
    ) -> order_models_pb2.Booking:
        new_booking = task.booking

        booking_response = await self._client.create_booking(
            _fill_pax_details(offer_details.quote, task),
        )

        new_booking.MergeFrom(
            order_models_pb2.Booking(
                status=order_models_pb2.Booking.STATUS_CONFIRMED,
                total_price=money.from_string(
                    string_amount=str(
                        booking_response.booking.price.total_in_selected_currency,
                    ),
                    currency=money.Currency(booking_response.booking.selected_currency),
                ).protobuf(),
                trip_result=order_models_pb2.TripBooking(
                    provider_booking_reference=str(booking_response.booking.identifier),
                    record_locator=booking_response.booking.booking_reference,
                    created_at=protobuf.datetime_to_protobuf(
                        booking_response.booking.created_date_time.replace(
                            tzinfo=datetime.timezone.utc,
                        ),
                    ),
                ),
                raw_data="{{confirmBooking: {0}}}".format(booking_response.json()),
            ),
        )

        return new_booking


def _fill_pax_details(
    quote_obj: quote.Quote,
    task: order_amqp_pb2.PlaceOrderTask,
) -> quote.Quote:
    number = phonenumbers.parse(task.contact_details.phone.e164_number)

    for leg_obj in quote_obj.legs:
        if len(leg_obj.passengers) != len(task.passengers):
            raise PassengerCountNotMatchingError

        pax_pairs = zip(leg_obj.passengers, task.passengers, strict=True)

        for quote_passenger, order_passenger in pax_pairs:
            quote_passenger.first_name = order_passenger.first_name
            quote_passenger.sur_name = order_passenger.last_name
            quote_passenger.email = task.contact_details.email
            quote_passenger.telephone = "+{country_code}{national_number}".format(
                country_code=str(number.country_code),
                national_number=str(number.national_number),
            )

            if order_passenger.HasField("doc_details"):
                _fill_doc_details(quote_passenger, order_passenger.doc_details)

    return quote_obj


def _fill_doc_details(
    quote_passenger: passenger.Passenger,
    doc_details: models_pb2.DocumentDetails,
) -> None:
    if doc_details.nationality:
        quote_passenger.nationality = doc_details.nationality

    if doc_details.HasField("exp_date"):
        quote_passenger.passport_expiry_date = protobuf.protobuf_to_date(
            doc_details.exp_date,
        ).isoformat()

    if doc_details.document_number:
        quote_passenger.passport_number = doc_details.document_number

    if doc_details.issue_county:
        quote_passenger.passport_place_of_issue = doc_details.issue_county

    if doc_details.HasField("issue_date"):
        quote_passenger.passport_start_date = protobuf.protobuf_to_date(
            doc_details.issue_date,
        ).isoformat()
