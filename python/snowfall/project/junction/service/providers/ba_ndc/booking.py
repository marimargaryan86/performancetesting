import more_itertools
import pycountry

from snowfall.project.junction.go.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.ba_ndc import (
    ba_ndc_helpers,
    cache,
    criteria,
    enums,
    notifications,
)
from snowfall.stdlib.v1 import postal_address_pb2
from snowfall.vendor.ba_ndc import client, errors
from snowfall.vendor.ba_ndc.adapters.order_view_adapter import OrderViewAdapter
from snowfall.vendor.ba_ndc.builders.order_request import OrderRequestBuilder
from snowfall.vendor.ba_ndc.models import (
    payer_details,
    request_order_schemas,
    response_common_passenger_schemas,
)
from snowfall.vendor.ba_ndc.models.util import passenger_enums

_PASSPORT_DOCUMENT_TYPE = "PT"


def _format_country(
    country_code: str,
) -> str:
    if country_code:
        country_obj = pycountry.countries.get(alpha_2=country_code)

        if country_obj:
            return country_obj.alpha_3

    return ""


def _get_residence_address(
    residence_address: postal_address_pb2.PostalAddress | None,
    *,
    return_flight_to_usa: bool,
) -> payer_details.Address | None:
    if residence_address is not None and return_flight_to_usa:
        return payer_details.Address(
            address_lines=list(residence_address.address_lines),
            city=residence_address.locality,
            zip_code=residence_address.postal_code,
            country_code=_format_country(residence_address.region_code),
        )

    return None


def _get_passport_document(
    passenger: models_pb2.Passenger,
    *,
    is_international_flight: bool,
) -> request_order_schemas.IdentityDocument | None:
    is_passport = (
        passenger.doc_details.document_type == models_pb2.DocumentDetails.TYPE_PASSPORT
    )

    if is_passport and is_international_flight:
        return request_order_schemas.IdentityDocument(
            document_number=passenger.doc_details.document_number,
            document_type=_PASSPORT_DOCUMENT_TYPE,
            birth_date=ba_ndc_helpers.proto_to_date(passenger.date_of_birth),
            nationality=_format_country(passenger.doc_details.nationality),
            issuing_country=_format_country(
                passenger.doc_details.issue_county,
            ),
            expiration_date=ba_ndc_helpers.proto_to_date(
                passenger.doc_details.exp_date,
            ),
            residence_country_code=(
                _format_country(
                    passenger.doc_details.residence_country_code,
                )
                if passenger.doc_details.residence_country_code
                else None
            ),
        )

    return None


class BookingHandler(object):
    _poll_retries_limit = 10
    _wait_time_between_polling = 15

    def __init__(
        self,
        ba_ndc_client: client.BaNdcClient,
        notifier: notifications.Notifier,
    ):
        self._client = ba_ndc_client
        self._logger = ba_ndc_helpers.get_logger(__name__)
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
                    provider_total_price=ba_ndc_helpers.parse_price(
                        booking_adapter.get_order().price,
                    ),
                    trip_result=models_pb2.TripBooking(
                        provider_booking_reference=str(
                            booking_adapter.get_booking_result().identifier,
                        ),
                        record_locator=booking_adapter.get_pnr(),
                        operator_booking_references=(
                            [booking_adapter.get_pnr()]
                            if booking_adapter.get_pnr()
                            else []
                        ),
                        created_at=ba_ndc_helpers.date_to_proto_now(),
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
        number = ba_ndc_helpers.parse_phone_number(
            task.contact_details.phone.e164_number,
        )
        order_request = OrderRequestBuilder(details.offer_id)

        for index, passenger in enumerate(task.passengers):
            passport_document = _get_passport_document(
                passenger=passenger,
                is_international_flight=details.international_flight,
            )

            order_request.add_passenger(
                request_order_schemas.PassengerExtended(
                    identifier=details.passengers[index].identifier,
                    passenger_type=criteria.get_passenger_type_enum(
                        ba_ndc_helpers.proto_to_date(passenger.date_of_birth),
                        ba_ndc_helpers.get_last_travel_date(task),
                    ),
                    first_name=passenger.first_name,
                    last_name=passenger.last_name,
                    name_title=models_pb2.Passenger.Title.Name(passenger.title)[
                        6:
                    ].upper(),
                    gender=enums.gender_from_proto(passenger.gender),
                    birth_date=ba_ndc_helpers.proto_to_date(passenger.date_of_birth),
                    contact=response_common_passenger_schemas.Contact(
                        email=task.contact_details.email,
                        phone=response_common_passenger_schemas.Phone(
                            phone_type=passenger_enums.PhoneTypeEnum.mobile,
                            number="+{country_code}{national_number}".format(
                                country_code=str(number.country_code),
                                national_number=str(number.national_number),
                            ),
                        ),
                    ),
                    identity_documents=(
                        [passport_document]
                        if passport_document and details.international_flight
                        else []
                    ),
                ),
            )

            order_request.residence_address = _get_residence_address(
                residence_address=task.residence_address,
                return_flight_to_usa=details.return_flight_to_usa,
            )

        order_request.set_cash_payment_info(
            more_itertools.first(details.passengers).identifier,
            details.price.currency,
            ba_ndc_helpers.str_to_decimal(details.price.amount),
        )

        adapter = OrderViewAdapter(
            await self._client.create_order(order_request.build()),
        )

        try:
            # TODO: this should be handled in a separate service
            await self._notifier.send(
                notifications.BookingNotification(task.metadata, adapter),
            )
        except notifications.NotificationError:
            self._logger.exception()

        return adapter
