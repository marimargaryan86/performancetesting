from __future__ import annotations

import datetime
import zoneinfo
from collections.abc import Iterable
from typing import Any, ClassVar, Literal

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
from snowfall.project.pay.service.companies.v1alpha import (
    models_pb2 as companies_models_pb2,
)
from snowfall.project.pay.service.currencies.v1alpha import (
    models_pb2 as currencies_models_pb2,
)
from snowfall.project.pay.service.refunds.v1alpha.models_pb2 import Refund
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transaction_models_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.currency_cloud.models import balance as balance_models

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
        relationships: dict[str, models.Relationship] = {}
        if company.account_id:
            relationships["account"] = {
                "data": models.ResourceIdentifier(
                    id=company.account_id,
                    type="accounts",
                ),
            }

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
                },
                "fxMarkup": round(company.fx_markup, 3),
                "processingMarkup": round(company.processing_markup, 3),
                "salesMarkup": round(company.sales_markup, 3),
                "resellerMarkups": [
                    Money.from_proto(reseller_markup)
                    for reseller_markup in company.reseller_markups
                ],
                "paymentType": protobuf.enum_value_to_slug(
                    companies_models_pb2.PaymentType.DESCRIPTOR,
                    company.payment_type,
                ),
                "paymentMethod": protobuf.enum_value_to_slug(
                    companies_models_pb2.PaymentMethod.DESCRIPTOR,
                    company.payment_method,
                ),
            },
            relationships=relationships,
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Company",
                        companyId=company.id,
                    ),
                ),
            },
        )


class AccountResource(models.Resource):
    api_type: ClassVar[str] = "accounts"

    @classmethod
    def from_proto(
        cls,
        account: companies_models_pb2.Account,
        request: requests.Request,
    ) -> AccountResource:
        relationships: dict[str, Any] = {
            "company": {"data": None},
            "contact": {"data": None},
        }
        if account.company_id:
            relationships["company"] = {
                "data": {
                    "id": account.company_id,
                    "type": "companies",
                },
            }
        if account.contact_id:
            relationships["contact"] = {
                "data": {
                    "id": account.contact_id,
                    "type": "contacts",
                },
            }
        return cls(
            id=account.id,
            type=AccountResource.api_type,
            attributes={
                "name": account.name,
                "status": protobuf.enum_value_to_slug(
                    companies_models_pb2.Status.DESCRIPTOR,
                    account.status,
                ),
            },
            relationships=relationships,
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Account",
                        accountId=account.id,
                    ),
                ),
            },
        )


class BeneficiariesResource(models.Resource):
    api_type: ClassVar[str] = "beneficiaries"

    @classmethod
    def from_models(
        cls,
        beneficiary: companies_models_pb2.Beneficiary,
        request: requests.Request,
    ) -> BeneficiariesResource:
        meta_data = beneficiary.meta_data
        bank_details = meta_data.bank_details
        beneficiary_address = meta_data.beneficiary_address
        return cls(
            id=beneficiary.id,
            type=BeneficiariesResource.api_type,
            attributes={
                "bankAccountHolderName": meta_data.bank_account_holder_name,
                "email": meta_data.email,
                "beneficiaryAddress": {
                    "addressLines": list(beneficiary_address.address_lines),
                    "countryCode": beneficiary_address.region_code,
                    "postalCode": beneficiary_address.postal_code or "",
                    "city": beneficiary_address.locality,
                    "state": beneficiary_address.administrative_area,
                },
                "bankDetails": {
                    **(
                        {
                            "accountNumber": bank_details.account_number,
                            "aba": bank_details.aba,
                        }
                        if bank_details.account_number
                        else {
                            "iban": bank_details.iban,
                        }
                    ),
                    "name": bank_details.name,
                    "bicSwift": bank_details.bic_swift,
                    "accountType": bank_details.account_type,
                    "paymentTypes": bank_details.payment_types,
                    "address": {
                        "addressLines": list(bank_details.address.address_lines),
                        "countryCode": bank_details.address.region_code,
                    },
                },
            },
            relationships={
                "account": {
                    "data": models.ResourceIdentifier(
                        id=beneficiary.account_id,
                        type="accounts",
                    ),
                },
                "currency": {
                    "data": models.ResourceIdentifier(
                        id=beneficiary.currency,
                        type="currencies",
                    ),
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Beneficiary",
                        beneficiaryId=beneficiary.id,
                    ),
                ),
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
                "conversion": {
                    "data": (
                        models.ResourceIdentifier(
                            id=transaction.conversion_id,
                            type="conversions",
                        )
                        if transaction.conversion_id
                        else None
                    ),
                },
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


class ConversionResource(models.Resource):
    api_type: ClassVar[str] = "conversions"

    @classmethod
    def from_proto(
        cls,
        conversion: transaction_models_pb2.Conversion,
        fx_delta: float | None,
        transaction_id: str | None,
        request: requests.Request,
    ) -> ConversionResource:
        conversion_resource = cls(
            id=conversion.id,
            type=ConversionResource.api_type,
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Conversion",
                        conversionId=conversion.id,
                    ),
                ),
            },
        )
        if conversion.status == conversion.Status.STATUS_FAILED:
            attributes = {
                "createdAt": protobuf.protobuf_to_datetime(
                    conversion.created_at,
                ),
                "buyAmount": Money.from_proto(conversion.buy_amount),
                "executedRate": round(conversion.executed_rate, 3),
                "fxStatus": protobuf.enum_value_to_slug(
                    conversion.Status.DESCRIPTOR,
                    conversion.status,
                ),
            }
        else:
            attributes = {
                "createdAt": protobuf.protobuf_to_datetime(
                    conversion.created_at,
                ),
                "settledAt": protobuf.protobuf_to_datetime(
                    conversion.settlement_date,
                ),
                "sellAmount": Money.from_proto(conversion.sell_amount),
                "buyAmount": Money.from_proto(conversion.buy_amount),
                "executedRate": round(conversion.executed_rate, 3),
                "fxDelta": fx_delta,
                "fxStatus": protobuf.enum_value_to_slug(
                    conversion.Status.DESCRIPTOR,
                    conversion.status,
                ),
            }
        conversion_resource.attributes = attributes
        if transaction_id is not None:
            conversion_resource.relationships = {
                "transactions": {
                    "data": models.ResourceIdentifier(
                        id=transaction_id,
                        type=Transaction.api_type,
                    ),
                },
            }
        return conversion_resource


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


class BalanceResource(models.Resource):
    api_type: ClassVar[str] = "balances"

    @classmethod
    def from_model(
        cls,
        balance: balance_models.BalanceResponse,
    ) -> BalanceResource:
        return cls(
            id=balance.identifier,
            type=BalanceResource.api_type,
            attributes={
                "amount": money.from_string(
                    balance.amount,
                    money.Currency(balance.currency),
                ).amount,
            },
            relationships={
                "account": {
                    "data": models.ResourceIdentifier(
                        id=balance.account_id,
                        type="accounts",
                    ),
                },
                "currency": {
                    "data": models.ResourceIdentifier(
                        id=balance.currency,
                        type="currencies",
                    ),
                },
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
                "refundedUs": Money.from_proto(refund.refunded_us),
                "refundedReseller": Money.from_proto(
                    refund.refunded_reseller,
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
            },
            relationships={
                "transaction": {
                    "data": models.ResourceIdentifier(
                        id=refund.transaction_id,
                        type="transactions",
                    ),
                },
                "conversion": {
                    "data": (
                        models.ResourceIdentifier(
                            id=refund.conversion_id,
                            type="conversions",
                        )
                        if refund.conversion_id
                        else None
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
                "currency": refund_position.currency.code,
                "amount": refund_position.amount,
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
