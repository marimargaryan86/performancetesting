import datetime
import decimal
import pathlib
from collections.abc import Callable, Mapping

import httpx
from dateutil import relativedelta

from snowfall.project.junction.rocket.service.bookings.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.project.junction.rocket.service.providers.silverrail import (
    cache,
    xml_serialization,
)
from snowfall.stdlib import money, sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.amqp import consumer, producer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.silverrail import client, errors
from snowfall.vendor.silverrail.models import booking as booking_models


class BookingFailedError(Exception):
    """Raised when not possible to continue booking because of an error."""

    def __init__(self, booking: models_pb2.Booking):
        self.booking = booking


class RequiredInformationMissingError(Exception):
    """Raised when required field is not available on the time of booking."""


class BookingRequestFailedError(Exception):
    """Raised when booking request is unsuccessful."""


class PassengerInformationValidator:
    def __init__(
        self,
        passenger: models_pb2.Passenger,
        leg_solution: booking_models.LegSolutionType,
    ):
        self._passenger = passenger
        self._leg_solution = leg_solution

    def validate(self) -> None:
        required = self._leg_solution.passenger_information_required
        if required is None:
            return

        for info in required.passenger_information:
            if info.type_value is None:
                continue
            validator = self._get_validator(info.type_value)
            if validator:
                validator(info)

    def validate_name(self, info: booking_models.PassengerInformationType) -> None:
        if not self._passenger.first_name:
            raise RequiredInformationMissingError("FirstName")
        if not self._passenger.last_name:
            raise RequiredInformationMissingError("LastName")

    def validate_email(self, info: booking_models.PassengerInformationType) -> None:
        if not self._passenger.contact_details.email:
            raise RequiredInformationMissingError("Email")

    def validate_address(self, info: booking_models.PassengerInformationType) -> None:
        if not "".join(self._passenger.contact_details.address.address_lines):
            raise RequiredInformationMissingError("Address")

    def validate_phone(self, info: booking_models.PassengerInformationType) -> None:
        if not self._passenger.contact_details.phone.e164_number:
            raise RequiredInformationMissingError("Phone")

    def validate_title(self, info: booking_models.PassengerInformationType) -> None:
        if not self._passenger.title:
            raise RequiredInformationMissingError("Title")

    def validate_place_of_birth(
        self,
        info: booking_models.PassengerInformationType,
    ) -> None:
        raise RequiredInformationMissingError("PlaceOfBirth")

    def validate_residence_info(
        self,
        info: booking_models.PassengerInformationType,
    ) -> None:
        if not self._passenger.doc_details.residence_country_code:
            raise RequiredInformationMissingError(
                "ResidenceInformation/residence_country_code",
            )

    def validate_gender(self, info: booking_models.PassengerInformationType) -> None:
        if not self._passenger.gender:
            raise RequiredInformationMissingError("Gender")

    def validate_dob(self, info: booking_models.PassengerInformationType) -> None:
        if self._passenger.date_of_birth is None:
            raise RequiredInformationMissingError("DateOfBirth")

    def validate_documents(self, info: booking_models.PassengerInformationType) -> None:
        type_passport = booking_models.PassengerInformationTypeAcceptableFormOfTravelDocument.PASSPORT
        passenger_doc_type = self._passenger.doc_details.document_type
        for doc in info.acceptable_form_of_travel_document:
            if doc != type_passport:
                raise RequiredInformationMissingError(
                    "Document: {0}".format(doc.value),
                )
            if passenger_doc_type != models_pb2.DocumentDetails.TYPE_PASSPORT:
                raise RequiredInformationMissingError("Document: Passport")

    def _get_validator(
        self,
        type_value: booking_models.PassengerInformationTypeType,
    ) -> Callable[[booking_models.PassengerInformationType], None] | None:
        return {
            booking_models.PassengerInformationTypeType.PASSENGER_NAME: self.validate_name,
            booking_models.PassengerInformationTypeType.PASSENGER_EMAIL: self.validate_email,
            booking_models.PassengerInformationTypeType.PASSENGER_TITLE: self.validate_title,
            booking_models.PassengerInformationTypeType.PASSENGER_PHONE: self.validate_phone,
            booking_models.PassengerInformationTypeType.PASSENGER_ADDRESS: self.validate_address,
            booking_models.PassengerInformationTypeType.PLACE_OF_BIRTH: self.validate_place_of_birth,
            booking_models.PassengerInformationTypeType.RESIDENCE_INFORMATION: self.validate_residence_info,
            booking_models.PassengerInformationTypeType.GENDER: self.validate_gender,
            booking_models.PassengerInformationTypeType.DATE_OF_BIRTH: self.validate_dob,
            booking_models.PassengerInformationTypeType.TRAVEL_DOCUMENTS: self.validate_documents,
        }.get(type_value)


class Booker:
    def __init__(
        self,
        quote_cache: cache.QuoteCache,
        booking_storage: filesystem.Storage,
        silverrail_client: client.SilverrailClient,
        provider_id: str,
        provider_name: str,
    ):
        self._quote_cache = quote_cache
        self._storage = booking_storage
        self._client = silverrail_client
        self._provider_id = provider_id
        self._provider_name = provider_name
        self._logger = stdout.get_logger()

    async def book(self, task: amqp_pb2.PlaceBookingTask) -> models_pb2.Booking:
        price_quote = await self._quote_cache.fetch(
            task.booking.trip_option.price_quote_id,
        )
        if not price_quote:
            raise cache.QuoteNotFoundError()

        task_booking = task.booking
        try:
            response = await self._create_booking(price_quote, task_booking)
        except BookingFailedError as create_booking_error:
            return create_booking_error.booking

        booking_reference = sequence.to_composite_id([
            order.order_id
            for order in response.booking_record.orders.order  # type: ignore[union-attr]
            if order.order_id
        ])

        try:
            booking = self._response_to_booking(
                response,
                booking_reference,
                task_booking,
            )
        except BookingFailedError as new_booking_error:
            return new_booking_error.booking
        task_booking.MergeFrom(booking)

        confirmation_at_payment_required = bool(
            response.booking_record.payment_requirements.confirmation_upon_add_payment,  # type: ignore[union-attr]
        )
        information_required = any(
            order.confirmation_information_required
            for order in response.booking_record.orders.order  # type: ignore[union-attr]
        )

        try:
            await self._add_payment(
                task_booking,
                confirmation_required=confirmation_at_payment_required,
                information_required=information_required,
            )
        except BookingFailedError as add_payment_error:
            return add_payment_error.booking

        # TODO(hovhannes.d): Do we need to check the status before confirming?
        if not confirmation_at_payment_required:
            try:
                await self._confirm_booking(
                    booking.provider_booking.record_locator,
                    response,
                    task_booking,
                )
            except BookingFailedError as confirmation_failed_error:
                return confirmation_failed_error.booking

        await self._storage.put(
            pathlib.Path(booking_reference),
            protobuf.AnySerializer[models_pb2.Booking].serialize(task_booking),
        )

        return task_booking

    async def _create_booking(
        self,
        price_quote: cache.PriceQuote,
        task_booking: models_pb2.Booking,
    ) -> booking_models.CreateBookingRecordResponse:
        exception_kwargs = {
            "passengers": price_quote.passengers,
            "ptp_price": price_quote.ptp_price,
            "leg_solution": price_quote.leg_solution,
            "booking_id": task_booking.id,
        }

        # TODO(hovhannes.d): Sync with product to know which delivery methods should we
        #  use. Might be needed to filter offers on search stage, to not check it here.
        self._validate_etk_supported(price_quote, task_booking)
        response = await self._request_booking(price_quote, task_booking)

        if not response.booking_record:
            self._logger.error(
                "Booking record is missing",
                **exception_kwargs,
            )
            task_booking.status = models_pb2.Booking.STATUS_ERROR
            task_booking.provider_booking.raw_data = xml_serialization.serialize(
                response,
            )
            raise BookingFailedError(task_booking)

        if not response.booking_record.orders:
            self._logger.error(
                "Order information is missing",
                **exception_kwargs,
            )
            task_booking.status = models_pb2.Booking.STATUS_ERROR
            task_booking.provider_booking.raw_data = xml_serialization.serialize(
                response,
            )
            raise BookingFailedError(task_booking)

        if not response.booking_record.payment_requirements:
            self._logger.error(
                "Payment requirements information is missing",
                **exception_kwargs,
            )
            task_booking.status = models_pb2.Booking.STATUS_ERROR
            task_booking.provider_booking.raw_data = xml_serialization.serialize(
                response,
            )
            raise BookingFailedError(task_booking)

        return response

    async def _request_booking(
        self,
        price_quote: cache.PriceQuote,
        task_booking: models_pb2.Booking,
    ) -> booking_models.CreateBookingRecordResponse:
        passengers = self._get_passengers(price_quote, task_booking)
        exception_kwargs = {
            "passengers": price_quote.passengers,
            "ptp_price": price_quote.ptp_price,
            "leg_solution": price_quote.leg_solution,
            "booking_id": task_booking.id,
        }
        try:
            response = await self._client.create_booking_record(
                passengers=passengers,
                leg_solution=booking_models.LegSolutionsType(
                    leg_solution=[price_quote.booking_leg_solution],
                ),
                prices=booking_models.CreateBookingRecordRequestType.Prices(
                    point_to_point_price=[price_quote.booking_ptp_price],
                ),
            )
        except (httpx.HTTPError, errors.SilverrailUnexpectedFormatError) as ex:
            self._logger.exception(
                "Failed to create booking",
                **exception_kwargs,
            )

            task_booking.status = models_pb2.Booking.STATUS_ERROR
            task_booking.provider_booking.raw_data = repr(ex)

            raise BookingFailedError(task_booking) from ex

        if not response.request_status or not response.request_status.success:
            self._logger.error("Booking request failed")
            task_booking.status = models_pb2.Booking.STATUS_ERROR
            task_booking.provider_booking.raw_data = xml_serialization.serialize(
                response,
            )
            raise BookingFailedError(task_booking)
        return response

    def _get_passengers(
        self,
        price_quote: cache.PriceQuote,
        booking: models_pb2.Booking,
    ) -> booking_models.CreateBookingRecordRequestType.Passengers:
        exception_kwargs = {
            "passengers": price_quote.passengers,
            "ptp_price": price_quote.ptp_price,
            "leg_solution": price_quote.leg_solution,
            "booking_id": booking.id,
        }
        age_ref_map = {
            passenger.age: passenger.passenger_spec_id
            for passenger in price_quote.passengers.passenger
            if passenger.age and passenger.passenger_spec_id
        }
        try:
            return booking_models.CreateBookingRecordRequestType.Passengers(
                passenger=[
                    self._parse_passenger(
                        passenger,
                        age_ref_map,
                        price_quote.booking_leg_solution,
                    )
                    for passenger in booking.passengers
                ],
            )
        except RequiredInformationMissingError as exc:
            self._logger.exception(
                "Failed to create booking",
                **exception_kwargs,
            )
            booking.status = models_pb2.Booking.STATUS_ERROR
            booking.provider_booking.raw_data = repr(exc)

            raise BookingFailedError(booking) from exc

    def _validate_etk_supported(
        self,
        price_quote: cache.PriceQuote,
        booking: models_pb2.Booking,
    ) -> None:
        if not price_quote.ptp_price.ticketable_fares:
            ptp_price = xml_serialization.serialize(price_quote.ptp_price)
            self._logger.error(
                "Ticketable fare information is missing",
                ptp_price=ptp_price,
            )

            booking.status = models_pb2.Booking.STATUS_ERROR
            booking.provider_booking.raw_data = ptp_price
            raise BookingFailedError(booking)

        for fare in price_quote.ptp_price.ticketable_fares.ticketable_fare:
            options = fare.ticketing_options_available
            ptp_price = xml_serialization.serialize(price_quote.ptp_price)
            if not options or not options.etk:
                self._logger.error(
                    "E-ticket not supported",
                    ptp_price=ptp_price,
                )
                booking.status = models_pb2.Booking.STATUS_ERROR
                booking.provider_booking.raw_data = ptp_price
                raise BookingFailedError(booking)

    async def _confirm_order(
        self,
        record_locator: str,
        order_id: str,
        booking: models_pb2.Booking,
    ) -> None:
        try:
            result = await self._client.confirm_booking(
                record_locator,
                order_id,
            )
        except (httpx.HTTPError, errors.SilverrailUnexpectedFormatError) as exc:
            self._logger.exception("Failed to confirm one of the orders")
            booking.status = models_pb2.Booking.STATUS_ERROR
            raise BookingFailedError(booking) from exc

        if not result.request_status or not result.request_status.success:
            self._logger.error("Failed to confirm one of the orders")
            booking.status = models_pb2.Booking.STATUS_ERROR
            raise BookingFailedError(booking)

    async def _confirm_booking(
        self,
        record_locator: str,
        booking_response: booking_models.CreateBookingRecordResponse,
        booking: models_pb2.Booking,
    ) -> None:
        # TODO(hovhannes.d): make this async gather.
        for order in booking_response.booking_record.orders.order:  # type: ignore[union-attr]
            if not order.order_id:
                self._logger.error("OrderID is missing")
                booking.status = models_pb2.Booking.STATUS_ERROR
                raise BookingFailedError(booking)

            await self._confirm_order(record_locator, order.order_id, booking)

    async def _add_payment(
        self,
        booking: models_pb2.Booking,
        *,
        confirmation_required: bool,
        information_required: bool,
    ) -> booking_models.AddPaymentResponse:
        # TODO(hovhannes.d): Sync with product and check payment type and account etc.
        payment = booking_models.AbstractPaymentRequestType.Payment(
            form_of_payment=booking_models.FormOfPaymentType(
                value="NONE",
                type_value=booking_models.FormOfPaymentTypeType.OA,
                authenticate_payer_required=True,
            ),
            amount=booking_models.MoneyType(
                value=decimal.Decimal(booking.trip_option.price.units),
                currency=booking.trip_option.price.currency_code,
            ),
            on_account=booking_models.OnAccountType(
                number="7039937961194902",
                validation_code="0003",
                account_name="EUR",
            ),
        )

        # TODO(hovhannes.d): Check this with product. What to do in such case?
        if confirmation_required and information_required:
            self._logger.error("Confirmation information is required while absent")
            booking.status = models_pb2.Booking.STATUS_ERROR
            raise BookingFailedError(booking)

        try:
            response = await self._client.add_payment(
                booking.provider_booking.record_locator,
                payment,
                confirm_booking=confirmation_required,
            )
        except (httpx.HTTPError, errors.SilverrailUnexpectedFormatError) as exc:
            self._logger.exception("Payment request failed")
            booking.status = models_pb2.Booking.STATUS_ERROR
            raise BookingFailedError(booking) from exc

        if not response.request_status or not response.request_status.success:
            self._logger.error(
                "Adding payment unsuccessful",
                payment_response=xml_serialization.serialize(response),
            )
            booking.status = models_pb2.Booking.STATUS_ERROR
            raise BookingFailedError(booking)

        return response

    def _response_to_booking(
        self,
        response: booking_models.CreateBookingRecordResponse,
        booking_reference: str,
        task_booking: models_pb2.Booking,
    ) -> models_pb2.Booking:
        if not response.booking_record or not response.booking_record.revenue_total:
            self._logger.error("No booking record information")
            task_booking.status = models_pb2.Booking.STATUS_ERROR
            task_booking.provider_booking.raw_data = xml_serialization.serialize(
                response,
            )
            raise BookingFailedError(task_booking)

        revenue = response.booking_record.revenue_total
        if revenue.value is None or revenue.currency is None:
            self._logger.error("Revenue information is missing")
            task_booking.status = models_pb2.Booking.STATUS_ERROR
            task_booking.provider_booking.raw_data = xml_serialization.serialize(
                response,
            )
            raise BookingFailedError(task_booking)

        if response.record_locator is None:
            self._logger.error("Record locator is missing")
            task_booking.status = models_pb2.Booking.STATUS_ERROR
            task_booking.provider_booking.raw_data = xml_serialization.serialize(
                response,
            )
            raise BookingFailedError(task_booking)

        price = money.from_string(
            string_amount=str(revenue.value),
            currency=money.Currency(
                revenue.currency.upper(),
            ),
        )

        return models_pb2.Booking(
            status=models_pb2.Booking.STATUS_CONFIRMED,
            provider_id=self._provider_id,
            provider_name=self._provider_name,
            trip_option=models_pb2.TripOption(
                price=price.protobuf(),
            ),
            provider_booking=models_pb2.ProviderBooking(
                record_locator=response.record_locator,
                booking_reference=booking_reference,
                raw_data=xml_serialization.serialize(response),
            ),
        )

    def _parse_passenger(
        self,
        passenger: models_pb2.Passenger,
        age_id_map: Mapping[int, str],
        leg_solution: booking_models.LegSolutionType,
    ) -> booking_models.PassengerType:
        gender_map = {
            models_pb2.Passenger.GENDER_MALE: booking_models.GenderType.MALE,
            models_pb2.Passenger.GENDER_FEMALE: booking_models.GenderType.FEMALE,
        }
        age = (
            relativedelta.relativedelta(
                datetime.datetime.today(),  # noqa: DTZ002
                protobuf.protobuf_to_date(passenger.date_of_birth),
            ).years
            + 1
        )

        PassengerInformationValidator(passenger, leg_solution).validate()

        return booking_models.PassengerType(
            passenger_id=age_id_map[age],
            age_at_time_of_travel=age,
            dob=xml_serialization.date_to_xml(
                protobuf.protobuf_to_date(passenger.date_of_birth),
            ),
            residence_information=booking_models.ResidenceInformationType(
                country_code=passenger.doc_details.residence_country_code,
            ),
            address=booking_models.AddressType(
                address_type=booking_models.AddressTypeAddressType.UNKNOWN,
                address1="\n".join(passenger.contact_details.address.address_lines),
                email=passenger.contact_details.email,
                address2="\n".join(passenger.contact_details.address.address_lines),
                city=passenger.contact_details.address.locality,
                zip_code=passenger.contact_details.address.postal_code,
                country=passenger.doc_details.residence_country_code,
            ),
            title=protobuf.enum_value_to_slug(
                enum_descriptor=models_pb2.Passenger.Title.DESCRIPTOR,
                enum_value=passenger.title,
            ),
            name_first=passenger.first_name,
            name_last=passenger.last_name,
            contact_information=booking_models.CustomerType.ContactInformation(
                contact=[
                    booking_models.CustomerContactType(
                        contact_type=booking_models.CustomerContactTypeContactType.UNKNOWN,
                        contact_medium=booking_models.CustomerContactTypeContactMedium.EMAIL,
                        contact_info=passenger.contact_details.email,
                    ),
                    booking_models.CustomerContactType(
                        contact_type=booking_models.CustomerContactTypeContactType.UNKNOWN,
                        contact_medium=booking_models.CustomerContactTypeContactMedium.PHONE,
                        contact_info=passenger.contact_details.phone.e164_number,
                    ),
                ],
            ),
            gender=gender_map.get(passenger.gender),
            travel_documents=booking_models.PassengerType.TravelDocuments(
                travel_document=[
                    booking_models.TravelDocumentType(
                        document_number=passenger.doc_details.document_number,
                        document_type=booking_models.TravelDocumentTypeDocumentType.PASSPORT,
                        expiration_date=xml_serialization.date_to_xml(
                            protobuf.protobuf_to_date(passenger.doc_details.exp_date),
                        ),
                        issuing_authority=booking_models.TravelDocumentType.IssuingAuthority(
                            country_code=passenger.doc_details.issue_county,
                        ),
                    ),
                ],
            ),
        )


class Consumer:
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.PlaceBookingTask],
        producer_obj: producer.Producer,
        booker: Booker,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._booker = booker

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: amqp_types.Message[amqp_pb2.PlaceBookingTask],
    ) -> None:
        try:
            booking_result = await self._booker.book(message.body)
        except cache.QuoteNotFoundError:
            return

        await self._producer.publish(
            booking_result,
            routing_key="bookings.results.prices",
        )

        await message.ack()
