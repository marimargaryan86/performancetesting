from __future__ import annotations

import datetime
import zoneinfo
from collections.abc import Iterable, Sequence
from typing import ClassVar, Literal

import pydantic
from starlette import datastructures, requests

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.service.orders.v1 import (
    models_pb2 as order_models_pb2,
)
from snowfall.project.junction.go.service.resellers.v1 import (
    models_pb2 as reseller_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.plus.adapter import configuration_vectors
from snowfall.project.pay.service.companies.v1 import (
    models_pb2 as companies_models_pb2,
)
from snowfall.project.pay.service.currencies.v1 import (
    models_pb2 as currencies_models_pb2,
)
from snowfall.project.pay.service.refunds.v1.models_pb2 import Refund
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transaction_models_pb2,
)
from snowfall.service.authentication.v1 import identities_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import money_pb2

_SELF_HREF: Literal["self"] = "self"
_RELATIONSHIPS_FIELD: Literal["data"] = "data"


class Money(models.BaseModel):
    currency: str
    amount: int

    @classmethod
    def from_proto(cls, price: money_pb2.Money) -> Money:
        money_price = money.from_protobuf(price)

        return cls(
            currency=money_price.currency.code,
            amount=money_price.amount,
        )


class Point(models.BaseModel):
    ref: str
    name: str
    latitude: float
    longitude: float
    time_zone: str = pydantic.Field(alias="timeZone")

    @classmethod
    def from_proto(cls, point: models_pb2.Point) -> Point:
        return cls(
            ref=point.ref,
            name=point.name,
            latitude=point.coordinates.latitude,
            longitude=point.coordinates.longitude,
            timeZone=point.time_zone,
        )


class RouteIdentifiers(models.BaseModel):
    vendor: str
    operator: str | None = None


class CabinClassResource(models.Resource):
    api_type: ClassVar[str] = "cabin-classes"

    @classmethod
    def from_proto(
        cls,
        cabin_class: models_pb2.CabinClass.Type.ValueType,
        self_link: datastructures.URL,
    ) -> CabinClassResource:
        cabin_class_id = protobuf.enum_value_to_slug(
            enum_descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
            enum_value=cabin_class,
        )
        return cls(
            id=cabin_class_id,
            type=CabinClassResource.api_type,
            attributes={
                "name": cabin_class_id,
            },
            links={
                _SELF_HREF: str(self_link),
            },
        )


class LegTypeResource(models.Resource):
    api_type: ClassVar[str] = "leg-types"

    @classmethod
    def from_proto(
        cls,
        schedule_type: models_pb2.Schedule.Type.ValueType,
        self_link: datastructures.URL,
    ) -> LegTypeResource:
        schedule_type_id = protobuf.enum_value_to_slug(
            enum_descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
            enum_value=schedule_type,
        )
        return cls(
            id=schedule_type_id,
            type=LegTypeResource.api_type,
            attributes={
                "name": schedule_type_id,
            },
            links={
                _SELF_HREF: str(self_link),
            },
        )


class OfferSegmentLeg(models.BaseModel):
    origin: Point
    destination: Point
    departure_at: datetime.datetime = pydantic.Field(alias="departureAt")
    arrival_at: datetime.datetime = pydantic.Field(alias="arrivalAt")

    @classmethod
    def from_proto(cls, leg: offer_models_pb2.OfferSegmentLeg) -> OfferSegmentLeg:
        return cls(
            origin=Point.from_proto(leg.origin),
            destination=Point.from_proto(leg.destination),
            departureAt=protobuf.protobuf_to_datetime(leg.departure_at).astimezone(
                zoneinfo.ZoneInfo(leg.origin.time_zone),
            ),
            arrivalAt=protobuf.protobuf_to_datetime(leg.arrival_at).astimezone(
                zoneinfo.ZoneInfo(leg.destination.time_zone),
            ),
        )


class Price(models.BaseModel):
    currency: str
    amount: str

    @classmethod
    def from_proto(cls, price: money_pb2.Money) -> Price:
        money_price = money.from_protobuf(price)

        return cls(
            currency=money_price.currency.code,
            amount=str(money_price),
        )

    @classmethod
    def from_protos(cls, prices: Iterable[money_pb2.Money]) -> Price:
        money_price = money.total(
            [money.from_protobuf(price) for price in prices],
        )

        return cls(
            currency=money_price.currency.code,
            amount=str(money_price),
        )


class FareRule(models.BaseModel):
    title: str
    body: str

    @classmethod
    def from_proto(cls, rule: offer_models_pb2.FareRule) -> FareRule:
        return cls(
            title=rule.title,
            body=rule.body,
        )


class TripBookingResource(models.Resource):
    api_type: ClassVar[str] = "trip-bookings"

    @classmethod
    def from_proto(
        cls,
        booking: order_models_pb2.Booking,
        booking_cancellation: order_models_pb2.BookingCancellation | None,
        refund: Refund | None,
        request: requests.Request,
    ) -> TripBookingResource:
        return cls(
            id=booking.id,
            type=TripBookingResource.api_type,
            attributes={
                "totalPrice": Price.from_proto(
                    booking.total_price,
                ),
                "operatorBookingReferences": list(
                    booking.trip_result.operator_booking_references,
                ),
                "externalReference": booking.trip_result.record_locator,
                "ticketUrls": list(booking.ticket_urls),
                "rules": [
                    {
                        "title": FareRule.from_proto(booking).title,
                        "body": FareRule.from_proto(booking).body,
                    }
                    for booking in booking.trip_option.rules
                ],
            },
            relationships={
                "order": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=booking.order_id,
                        type="orders",
                    ),
                },
                "status": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            order_models_pb2.Booking.Status.DESCRIPTOR,
                            booking.status,
                        ),
                        type="booking-statuses",
                    ),
                },
                "details": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=details.id,
                            type="trip-booking-details",
                        )
                        for details in booking.trip_option.details
                    ],
                },
                "bookingCancellation": {
                    _RELATIONSHIPS_FIELD: (
                        models.ResourceIdentifier(
                            id=booking_cancellation.id,
                            type=BookingCancellationResource.api_type,
                        )
                        if booking_cancellation
                        else None
                    ),
                },
                "transaction": {
                    _RELATIONSHIPS_FIELD: (
                        models.ResourceIdentifier(
                            id=booking.transaction_id,
                            type=Transaction.api_type,
                        )
                        if booking.transaction_id
                        else None
                    ),
                },
                "refund": {
                    _RELATIONSHIPS_FIELD: (
                        models.ResourceIdentifier(
                            id=refund.id,
                            type=RefundsResource.api_type,
                        )
                        if refund
                        else None
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewBooking",
                        bookingId=booking.id,
                    ),
                ),
            },
        )


class TripBookingDetailsResource(models.Resource):
    api_type: ClassVar[str] = "trip-booking-details"

    @classmethod
    def from_proto(
        cls,
        details: order_models_pb2.TripOptionDetails,
        request: requests.Request,
    ) -> TripBookingDetailsResource:
        return cls(
            id=details.id,
            type=TripBookingDetailsResource.api_type,
            attributes={
                "cabinClassName": details.cabin_class.marketing_name,
                "vendor": details.segment.vendor,
                "operator": details.segment.operator or None,
                "routeIdentifiers": RouteIdentifiers(
                    vendor=details.segment.vehicle.number,
                    operator=None,
                ),
                "sequences": {
                    "trip": details.segment.trip_sequence,
                    "segment": details.segment.segment_sequence,
                },
                "legs": [
                    OfferSegmentLeg.from_proto(leg) for leg in details.segment.legs
                ],
            },
            relationships={
                "booking": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=details.booking_id,
                        type=TripBookingResource.api_type,
                    ),
                },
                "cabinClass": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            enum_descriptor=models_pb2.CabinClass.Type.DESCRIPTOR,
                            enum_value=details.cabin_class.type,
                        ),
                        type=CabinClassResource.api_type,
                    ),
                },
                "legType": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=protobuf.enum_value_to_slug(
                            enum_descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
                            enum_value=details.segment.type,
                        ),
                        type=LegTypeResource.api_type,
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewBookingDetails",
                        bookingDetailsId=details.id,
                    ),
                ),
            },
        )


class JourneyResource(models.Resource):
    api_type: ClassVar[str] = "journeys"

    @classmethod
    def from_proto(
        cls,
        journey: order_models_pb2.Journey,
        request: requests.Request,
    ) -> JourneyResource:
        return cls(
            id=journey.id,
            type=JourneyResource.api_type,
            attributes={
                "createdAt": protobuf.protobuf_to_datetime(journey.created_at),
                "reference": journey.passenger_name_record,
                "contactDetails": {
                    "email": journey.contact_details.email,
                    "address": {
                        "addressLines": list(
                            journey.contact_details.address.address_lines,
                        ),
                        "countryCode": journey.contact_details.address.region_code,
                        "postalCode": journey.contact_details.address.postal_code,
                        "city": journey.contact_details.address.locality,
                    },
                    "phoneNumber": journey.contact_details.phone.e164_number,
                },
            },
            relationships={
                "orders": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=order.id,
                            type="orders",
                        )
                        for order in journey.orders
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewJourney",
                        journeyId=journey.id,
                    ),
                ),
            },
        )


class OrderResource(models.Resource):
    api_type: ClassVar[str] = "orders"

    @classmethod
    def from_proto(
        cls,
        order: order_models_pb2.Order,
        request: requests.Request,
    ) -> OrderResource:
        return cls(
            id=order.id,
            type=OrderResource.api_type,
            attributes={
                "createdAt": protobuf.protobuf_to_datetime(order.created_at),
                "passengers": [
                    {
                        "firstName": passenger.first_name,
                        "dateOfBirth": protobuf.protobuf_to_date(
                            passenger.date_of_birth,
                        ),
                        "title": protobuf.enum_value_to_slug(
                            enum_descriptor=order_models_pb2.Passenger.Title.DESCRIPTOR,
                            enum_value=passenger.title,
                        ),
                        "lastName": passenger.last_name,
                        "gender": protobuf.enum_value_to_slug(
                            enum_descriptor=order_models_pb2.Passenger.Gender.DESCRIPTOR,
                            enum_value=passenger.gender,
                        ),
                    }
                    for passenger in order.passengers
                ],
            },
            relationships={
                "journey": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=order.journey_id,
                        type=JourneyResource.api_type,
                    ),
                },
                "bookings": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=booking.id,
                            type=TripBookingResource.api_type,
                        )
                        for booking in order.bookings
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewOrder",
                        orderId=order.id,
                    ),
                ),
            },
        )


class ActivityResource(models.Resource):
    api_type: ClassVar[str] = "activities"

    @classmethod
    def from_proto(
        cls,
        transaction: transaction_models_pb2.Transaction,
        order: order_models_pb2.Order,
        booking: order_models_pb2.Booking,
        company: companies_models_pb2.Company,
        reseller: reseller_models_pb2.Reseller,
        request: requests.Request,
    ) -> ActivityResource:
        return cls(
            id=transaction.id,
            type=ActivityResource.api_type,
            attributes={
                "transactionCreatedAt": protobuf.protobuf_to_date(
                    transaction.created_at,
                ),
                "departureAt": protobuf.protobuf_to_date(
                    booking.trip_option.details[0].segment.legs[0].departure_at,  # noqa: WPS219
                ),
                "baseConverted": Money.from_proto(transaction.amounts.base_converted),
                "salesMargin": Money.from_proto(transaction.amounts.sales_margin),
                "quotation": Money.from_proto(transaction.amounts.quotation),
                "taxConverted": Money.from_proto(transaction.amounts.tax_converted),
                "totalAmount": Money.from_proto(transaction.amounts.total_amount),
                "payerName": reseller.name,
                "fxMargin": Money.from_proto(transaction.amounts.fx_margin).amount,
                "processingMargin": money.from_protobuf(
                    transaction.amounts.processing_margin,
                ).amount,
                "feeAmount": Money.from_proto(transaction.amounts.fee_amount),
                "totalMarkups": Money.from_proto(transaction.amounts.total_markups),
                "beneficiaryAmount": Money.from_proto(transaction.amounts.beneficiary),
                "beneficiaryName": company.name,
                "passengerName": order.passengers[0].first_name,
                "paymentType": protobuf.enum_value_to_slug(
                    companies_models_pb2.PaymentType.DESCRIPTOR,
                    company.payment_type,
                ),
                "paymentMethod": protobuf.enum_value_to_slug(
                    companies_models_pb2.PaymentMethod.DESCRIPTOR,
                    company.payment_method,
                ),
                "fxMarkup": transaction.rates.fx_markup,
                "salesMarkup": transaction.rates.sales_markup,
                "processingMarkup": transaction.rates.processing_markup,
            },
            relationships={
                "invoiceReference": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=transaction.invoice_reference_id,
                        type="invoice-reference",
                    ),
                },
                "externalReference": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=transaction.external_reference_id,
                        type="external-reference",
                    ),
                },
                "order": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=order.id,
                        type="orders",
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Activity",
                        transactionId=transaction.id,
                    ),
                ),
            },
        )


class CancellationRequestResource(models.Resource):
    api_type: ClassVar[str] = "cancellation-request"

    @classmethod
    def from_proto(
        cls,
        cancellation_request: order_models_pb2.CancellationRequest,
        request: requests.Request,
    ) -> CancellationRequestResource:
        request_model = order_models_pb2.CancellationRequest
        status = protobuf.enum_value_to_slug(
            enum_descriptor=request_model.Status.DESCRIPTOR,
            enum_value=cancellation_request.status,
        )
        return cls(
            id=cancellation_request.id,
            type=cls.api_type,
            attributes={
                "status": status,
            },
            relationships={
                "bookings": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=booking_cancellation.booking_id,
                            type=TripBookingResource.api_type,
                        )
                        for booking_cancellation in cancellation_request.booking_cancellations
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewCancellationRequest",
                        cancellationRequestId=cancellation_request.id,
                    ),
                ),
            },
        )


class ContactResource(models.Resource):
    api_type: ClassVar[str] = "contacts"

    @classmethod
    def from_proto(
        cls,
        contact: companies_models_pb2.Contact,
    ) -> ContactResource:
        return cls(
            id=contact.id,
            type=ContactResource.api_type,
            attributes={
                "firstName": contact.first_name,
                "lastName": contact.last_name,
                "emailAddress": contact.email,
                "phoneNumber": contact.phone_number.e164_number,
            },
            relationships={
                "company": {
                    "data": models.ResourceIdentifier(
                        id=contact.company_id,
                        type="companies",
                    ),
                },
            },
        )


class Company(models.Resource):
    api_type: ClassVar[str] = "companies"

    @classmethod
    def from_proto(
        cls,
        company: companies_models_pb2.Company,
        request: requests.Request,
    ) -> Company:
        return cls(
            id=company.id,
            type=Company.api_type,
            attributes={
                "name": company.name,
                "address": {
                    "addressLines": list(company.address.address_lines),
                    "countryCode": company.address.region_code,
                    "postalCode": company.address.postal_code,
                    "city": company.address.locality,
                    "state": company.address.administrative_area,
                },
                "fxMarkup": round(company.fx_markup, 3),
                "processingMarkup": round(company.processing_markup, 3),
                "salesMarkup": round(company.sales_markup, 3),
                "feeAmounts": [
                    Money.from_proto(fee_amount) for fee_amount in company.fee_amounts
                ],
                "paymentType": protobuf.enum_value_to_slug(
                    companies_models_pb2.PaymentType.DESCRIPTOR,
                    company.payment_type,
                ),
                "paymentMethod": protobuf.enum_value_to_slug(
                    companies_models_pb2.PaymentMethod.DESCRIPTOR,
                    company.payment_method,
                ),
                "billingType": protobuf.enum_value_to_slug(
                    companies_models_pb2.BillingType.DESCRIPTOR,
                    company.billing_type,
                ),
                "applyMarkups": company.apply_markups,
                "invoiceGenerationFrequency": company.invoice_generation_frequency,
                "verticalFees": [
                    {
                        "verticalType": protobuf.enum_value_to_slug(
                            companies_models_pb2.VerticalType.DESCRIPTOR,
                            fee.vertical_type,
                        ),
                        "billingType": protobuf.enum_value_to_slug(
                            companies_models_pb2.BillingType.DESCRIPTOR,
                            fee.billing_type,
                        ),
                        "value": round(fee.value, 3),
                    }
                    for fee in company.vertical_fees
                ],
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Company",
                        companyId=company.id,
                    ),
                ),
            },
        )


class OnboardingToken(models.Resource):
    api_type: ClassVar[str] = "onboarding-tokens"

    @classmethod
    def from_values(
        cls,
        token: str,
    ) -> OnboardingToken:
        return cls(
            id=token,
            type=OnboardingToken.api_type,
            attributes={
                "token": token,
            },
        )


class OnboardingTokenCompanyDetails(models.Resource):
    api_type: ClassVar[str] = "onboarding-tokens"

    @classmethod
    def from_values(
        cls,
        token: str,
        company_name: str,
        customer_id: str,
    ) -> OnboardingTokenCompanyDetails:
        return cls(
            id=token,
            type=OnboardingTokenCompanyDetails.api_type,
            attributes={
                "companyName": company_name,
                "paymentReference": customer_id,
            },
        )


class Transaction(models.Resource):
    api_type: ClassVar[str] = "transactions"

    @classmethod
    def from_proto(
        cls,
        transaction: transaction_models_pb2.Transaction,
        request: requests.Request,
    ) -> Transaction:
        return cls(
            id=transaction.id,
            type=Transaction.api_type,
            attributes={
                "externalReference": transaction.external_reference_id,
                "invoiceReference": transaction.invoice_reference_id,
                "createdAt": protobuf.protobuf_to_datetime(transaction.created_at),
                "amounts": {
                    "beneficiary": Money.from_proto(
                        transaction.amounts.beneficiary,
                    ),
                    "quotation": Money.from_proto(transaction.amounts.quotation),
                    "baseConverted": Money.from_proto(
                        transaction.amounts.base_converted,
                    ),
                    "salesMargin": Money.from_proto(transaction.amounts.sales_margin),
                    "fxMargin": Money.from_proto(
                        transaction.amounts.fx_margin,
                    ),
                    "processingMargin": Money.from_proto(
                        transaction.amounts.processing_margin,
                    ),
                    "totalAmount": Money.from_proto(
                        transaction.amounts.total_amount,
                    ),
                },
                "rates": {
                    "fxQuote": round(transaction.rates.fx_quote, 3),
                    "fxBuffer": round(transaction.rates.fx_buffer, 3),
                    "salesMarkup": round(transaction.rates.sales_markup, 3),
                    "fxMarkup": round(transaction.rates.fx_markup, 3),
                    "processingMarkup": round(transaction.rates.processing_markup, 3),
                },
                "paymentType": protobuf.enum_value_to_slug(
                    companies_models_pb2.PaymentType.DESCRIPTOR,
                    transaction.payment_type,
                ),
                "paymentMethod": protobuf.enum_value_to_slug(
                    companies_models_pb2.PaymentMethod.DESCRIPTOR,
                    transaction.payment_method,
                ),
            },
            relationships={
                "payer": {
                    "data": models.ResourceIdentifier(
                        id=transaction.payer_id,
                        type="companies",
                    ),
                },
                "beneficiary": {
                    "data": models.ResourceIdentifier(
                        id=transaction.beneficiary_id,
                        type="companies",
                    ),
                },
                "bill": {
                    "data": (
                        models.ResourceIdentifier(
                            id=transaction.bill_id,
                            type="bills",
                        )
                        if transaction.bill_id
                        else None
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Transactions",
                        transactionId=transaction.id,
                    ),
                ),
            },
        )


class BookingCancellationResource(models.Resource):
    api_type: ClassVar[str] = "booking-cancellation"

    @classmethod
    def from_proto(
        cls,
        booking_cancellation: order_models_pb2.BookingCancellation,
        request: requests.Request,
    ) -> BookingCancellationResource:
        request_model = order_models_pb2.BookingCancellation
        status = protobuf.enum_value_to_slug(
            enum_descriptor=request_model.Status.DESCRIPTOR,
            enum_value=booking_cancellation.status,
        )
        return cls(
            id=booking_cancellation.id,
            type=cls.api_type,
            attributes={
                "status": status,
            },
            relationships={
                "booking": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=booking_cancellation.booking_id,
                        type=TripBookingResource.api_type,
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewBookingCancellationByBooking",
                        bookingId=booking_cancellation.booking_id,
                    ),
                ),
            },
        )


class BillResource(models.Resource):
    api_type: ClassVar[str] = "bills"

    @classmethod
    def from_proto(
        cls,
        bill: transaction_models_pb2.Bill,
        request: requests.Request,
    ) -> BillResource:
        return cls(
            id=bill.id,
            type=BillResource.api_type,
            attributes={
                "createdAt": protobuf.protobuf_to_datetime(
                    bill.created_at,
                ),
                "updatedAt": protobuf.protobuf_to_datetime(
                    bill.updated_at,
                ),
                "isReconciled": bill.is_reconciled,
                "totalAmount": (
                    money.from_protobuf(bill.total_amount)
                    if bill.HasField("total_amount")
                    else None
                ),
                "reconciledAmount": (
                    money.from_protobuf(bill.reconciled_amount)
                    if bill.HasField("reconciled_amount")
                    else None
                ),
            },
            relationships={
                "order": {
                    "data": models.ResourceIdentifier(
                        id=bill.order_id,
                        type="orders",
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Bills",
                        billId=bill.id,
                    ),
                ),
            },
        )


class RefundsResource(models.Resource):
    api_type: ClassVar[str] = "refunds"

    @classmethod
    def from_proto(
        cls,
        refund: Refund,
        request: requests.Request,
    ) -> RefundsResource:
        return cls(
            id=refund.id,
            type=RefundsResource.api_type,
            attributes={
                "status": protobuf.enum_value_to_slug(
                    Refund.Status.DESCRIPTOR,
                    refund.status,
                ),
                "refundReceived": refund.refund_received,
                "note": refund.note,
                "refundedUs": (
                    Money.from_proto(refund.refunded_us)
                    if refund.HasField("refunded_us")
                    else None
                ),
                "refundedReseller": (
                    Money.from_proto(refund.refunded_reseller)
                    if refund.HasField("refunded_reseller")
                    else None
                ),
                "refundedUsInPayerCurrency": (
                    Money.from_proto(
                        refund.refunded_us_in_payer_currency,
                    )
                    if refund.HasField("refunded_us_in_payer_currency")
                    else None
                ),
                "refundPosition": (
                    Money.from_proto(
                        refund.refund_position,
                    )
                    if refund.HasField("refund_position")
                    else None
                ),
                "invoiceReference": refund.invoice_reference,
                "externalReference": refund.external_reference_id,
            },
            relationships={
                "transaction": {
                    "data": models.ResourceIdentifier(
                        id=refund.transaction_id,
                        type="transactions",
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Refund",
                        refundId=refund.id,
                    ),
                ),
            },
        )


class RefundPosition(models.Resource):
    api_type: ClassVar[str] = "refund-position"

    @classmethod
    def from_models(
        cls,
        refund_id: str,
        refund_position: money.Money,
    ) -> RefundPosition:
        return cls(
            id=refund_id,
            type=RefundPosition.api_type,
            attributes={
                "refundPosition": refund_position,
            },
        )


class CurrenciesResource(models.Resource):
    api_type: ClassVar[str] = "currencies"

    @classmethod
    def from_model(
        cls,
        currency: currencies_models_pb2.Currency,
        request: requests.Request,
    ) -> CurrenciesResource:
        return cls(
            id=currency.code,
            type=CurrenciesResource.api_type,
            attributes={
                "name": currency.name,
                "minorUnits": currency.exponent or 0,
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Currencies",
                        currencyId=currency.code,
                    ),
                ),
            },
        )


class ResellerResource(models.Resource):
    api_type: ClassVar[str] = "resellers"

    @classmethod
    def from_proto(
        cls,
        reseller: reseller_models_pb2.Reseller,
        request: requests.Request,
    ) -> ResellerResource:
        return cls(
            id=reseller.id,
            type=ResellerResource.api_type,
            attributes={
                "name": reseller.name,
                "providers": list(reseller.provider_ids),
            },
            relationships={
                "company": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=reseller.company_id,
                        type="companies",
                    ),
                },
                "currency": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=reseller.default_currency,
                        type="currencies",
                    ),
                },
                "parentResellers": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=parent_reseller_id,
                            type="resellers",
                        )
                        for parent_reseller_id in reseller.parent_reseller_ids
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Reseller",
                        resellerId=reseller.id,
                    ),
                ),
            },
        )


class UserResource(models.Resource):
    api_type: ClassVar[str] = "users"

    @classmethod
    def from_proto(
        cls,
        identity: identities_pb2.Identity,
    ) -> UserResource:
        metadata = dict(identity.metadata_public.items())
        role = metadata.get("role", "")
        reseller_id = metadata.get("reseller_id", "")
        return cls(
            id=identity.id,
            type=UserResource.api_type,
            attributes={
                "email": identity.email,
                "role": role,
            },
            relationships={
                "reseller": {
                    _RELATIONSHIPS_FIELD: (
                        models.ResourceIdentifier(
                            id=str(reseller_id),
                            type=ResellerResource.api_type,
                        )
                        if reseller_id
                        else None
                    ),
                },
            },
        )


class UsersProfileResource(models.Resource):
    api_type: ClassVar[str] = "users-profiles"

    @classmethod
    def from_proto(
        cls,
        reseller_id: str,
        company: companies_models_pb2.Company,
        contacts: Sequence[companies_models_pb2.Contact],
    ) -> UsersProfileResource:
        return cls(
            id=reseller_id,
            type=UsersProfileResource.api_type,
            attributes={
                "company": {
                    "name": company.name,
                    "address": {
                        "addressLines": list(company.address.address_lines),
                        "countryCode": company.address.region_code,
                        "postalCode": company.address.postal_code,
                        "city": company.address.locality,
                        "state": company.address.administrative_area,
                    },
                },
                "contacts": [
                    {
                        "firstName": contact.first_name,
                        "lastName": contact.last_name,
                        "emailAddress": contact.email,
                        "phoneNumber": contact.phone_number.e164_number,
                    }
                    for contact in contacts
                ],
                "permissions": {},
            },
        )


class PlusServiceAccess(models.Resource):
    api_type: ClassVar[str] = "plus-services-access"

    @classmethod
    def from_dict(
        cls,
        permission: configuration_vectors.Permission,
    ) -> PlusServiceAccess:
        return cls(
            id=permission.ref,
            type=PlusServiceAccess.api_type,
            attributes={
                "ref": permission.ref,
                "displayName": permission.name,
                "enabled": permission.enabled,
            },
        )
