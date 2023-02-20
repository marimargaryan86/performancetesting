import datetime
import itertools

import more_itertools
import phonenumbers
import structlog

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.ba_ndc import (
    cache,
    criteria,
    enums,
    notifications,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ba_ndc import client, errors
from snowfall.vendor.ba_ndc.adapters.order_view_adapter import OrderViewAdapter
from snowfall.vendor.ba_ndc.builders.order_request import OrderRequestBuilder
from snowfall.vendor.ba_ndc.models import (
    payer_details,
    request_order_schemas,
    response_common_passenger_schemas,
)


def _get_last_travel_date(
    task: amqp_pb2.PlaceOrderTask,
) -> datetime.date:
    segments = itertools.chain(
        [tr.segment for tr in task.booking.trip_option.details],
    )

    return max(
        protobuf.protobuf_to_datetime(
            more_itertools.last(segment.legs).departure_at,
        ).date()
        for segment in segments
    )


def _get_destination_residence_details(
    international_flight: bool,
    return_flight_to_usa: bool,
    destination_det: models_pb2.DestinationResidenceDetails,
) -> payer_details.DestinationResidenceDetails | None:
    if destination_det is not None:
        drd = payer_details.DestinationResidenceDetails(
            residence_address=None,
            residence_country_code=None,
        )

        if international_flight and destination_det.residence_country_code is not None:
            drd.residence_country_code = destination_det.residence_country_code

        if return_flight_to_usa and destination_det.residence_address is not None:
            drd.residence_address = payer_details.Address(
                address_lines=list(
                    destination_det.residence_address.address_lines,
                ),
                city=destination_det.residence_address.locality,
                zip_code=destination_det.residence_address.postal_code,
                country_code=destination_det.residence_address.region_code,
            )

        return drd


class BookingHandler(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 15

    def __init__(
        self,
        ba_ndc_client: client.BaNdcClient,
        notifier: notifications.Notifier,
    ):
        self._client = ba_ndc_client
        self._logger = structlog.get_logger(__name__)
        self._notifier = notifier

    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> models_pb2.Booking:
        new_booking = task.booking

        try:
            booking_adapter: OrderViewAdapter = await self._make_booking(
                task=task,
                details=details,
            )
        except errors.ServiceError as error:
            self._logger.exception(
                "Booking failed",
                reason=repr(error),
            )

            new_booking.status = models_pb2.Booking.STATUS_ERROR
            new_booking.raw_data = repr(error)

            return new_booking

        if booking_adapter.is_success():
            new_booking.MergeFrom(
                models_pb2.Booking(
                    status=models_pb2.Booking.STATUS_CONFIRMED,
                    total_price=money.from_string(
                        string_amount=str(
                            booking_adapter.get_order().price.total_amount,
                        ),
                        currency=money.Currency(
                            booking_adapter.get_order().price.currency,
                        ),
                    ).protobuf(),
                    trip_result=models_pb2.TripBooking(
                        provider_booking_reference=str(
                            booking_adapter.get_booking_result().identifier,
                        ),
                        record_locator=booking_adapter.get_pnr(),
                        created_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.now(tz=datetime.timezone.utc),
                        ),
                    ),
                    raw_data=booking_adapter.get_booking_result().json(),
                ),
            )

        return new_booking

    async def _make_booking(  # noqa: WPS210
        self,
        task: amqp_pb2.PlaceOrderTask,
        details: cache.OfferDetails,
    ) -> OrderViewAdapter:
        number = phonenumbers.parse(task.contact_details.phone.e164_number)
        order_request = OrderRequestBuilder(details.offer_id)

        for index, passenger in enumerate(task.passengers):
            passport_document: request_order_schemas.IdentityDocument | None = None
            doc_details = passenger.doc_details

            if doc_details.document_type == 1 and details.doc_required:
                passport_document = request_order_schemas.IdentityDocument(
                    document_number=passenger.doc_details.document_number,
                    document_type="PT",
                    birth_date=protobuf.protobuf_to_date(passenger.date_of_birth),
                    nationality=passenger.doc_details.nationality,
                    issuing_country=passenger.doc_details.issue_county,
                    expiration_date=protobuf.protobuf_to_date(
                        passenger.doc_details.exp_date,
                    ),
                )

            order_request.add_passenger(
                request_order_schemas.PassengerExtended(
                    identifier=details.passengers[index].identifier,
                    passenger_type=criteria.get_passenger_type_enum(
                        protobuf.protobuf_to_date(passenger.date_of_birth),
                        _get_last_travel_date(task),
                    ),
                    first_name=passenger.first_name,
                    last_name=passenger.last_name,
                    name_title=models_pb2.Passenger.Title.Name(passenger.title)[
                        6:
                    ].upper(),
                    gender=enums.gender_from_proto(passenger.gender),
                    birth_date=protobuf.protobuf_to_date(passenger.date_of_birth),
                    contact=response_common_passenger_schemas.Contact(
                        email=task.contact_details.email,
                        phone=response_common_passenger_schemas.Phone(
                            phone_type=enums.passenger_enums.PhoneTypeEnum.mobile,
                            number="+{country_code}{national_number}".format(
                                country_code=str(number.country_code),
                                national_number=str(number.national_number),
                            ),
                        ),
                    ),
                    identity_documents=(
                        [passport_document]
                        if passport_document and details.doc_required
                        else []
                    ),
                ),
            )

            order_request.destination_residence_details = (
                _get_destination_residence_details(
                    details.international_flight,
                    details.return_flight_to_usa,
                    task.destination_residence_details,
                )
            )

        adapter = OrderViewAdapter(
            await self._client.create_order(order_request.build()),
        )

        try:
            # todo: this should be handled in a separate service
            await self._notifier.send(
                notifications.BookingNotification(task.metadata, adapter),
            )
        except notifications.NotificationError:
            self._logger.exception()

        return adapter
