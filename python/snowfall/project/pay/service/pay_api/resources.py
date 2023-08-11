from __future__ import annotations

from typing import Any, ClassVar

from starlette import requests

from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.project.pay.service.currencies.v1alpha.models_pb2 import (
    Currency as CurrencyModel,
)
from snowfall.project.pay.service.payments.v1alpha import models_pb2 as payment_models
from snowfall.project.pay.service.payments.v1alpha.models_pb2 import Payment
from snowfall.project.pay.service.refunds.v1alpha.models_pb2 import Refund
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transaction_models,
)
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import Conversion
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.currency_cloud.models import balance as balance_models

_SELF_HREF = "self"


class QuoteResource(models.Resource):
    api_type: ClassVar[str] = "quotes"

    @classmethod
    def from_proto(
        cls,
        quotation: transaction_models.Quotation,
        request: requests.Request,
    ) -> QuoteResource:
        return cls(
            id=quotation.id,
            type=QuoteResource.api_type,
            attributes={
                "amount": money.from_protobuf(quotation.amounts.quotation).amount,
                "tax": money.from_protobuf(quotation.amounts.tax).amount,
                "totalMarkups": money.from_protobuf(
                    quotation.amounts.total_markups,
                ).amount,
                "serviceMarkup": money.from_protobuf(
                    quotation.amounts.service_markup,
                ).amount,
                "totalAmount": money.from_protobuf(
                    quotation.amounts.total_amount,
                ).amount,
                "resellerMarkup": money.from_protobuf(
                    quotation.amounts.reseller_markup,
                ).amount,
                "leadCompanyMarkup": money.from_protobuf(
                    quotation.amounts.lead_reseller_markup,
                ).amount,
            },
            relationships={
                "fromCurrency": {
                    "data": {
                        "id": quotation.amounts.beneficiary.currency_code,
                        "type": "currencies",
                    },
                },
                "toCurrency": {
                    "data": {
                        "id": quotation.amounts.quotation.currency_code,
                        "type": "currencies",
                    },
                },
                "payer": {
                    "data": {
                        "id": quotation.payer_id,
                        "type": "companies",
                    },
                },
                "beneficiary": {
                    "data": {
                        "id": quotation.beneficiary_id,
                        "type": "companies",
                    },
                },
            },
        )


class Company(models.Resource):
    api_type: ClassVar[str] = "companies"

    @classmethod
    def from_proto(
        cls,
        company: models_pb2.Company,
        request: requests.Request,
    ) -> Company:
        relationships = {}
        if company.account_id:
            relationships["account"] = {
                "data": {
                    "id": company.account_id,
                    "type": "accounts",
                },
            }
        if company.lead_company_id:
            relationships["leadCompany"] = {
                "data": {
                    "id": company.lead_company_id,
                    "type": "lead-companies",
                },
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
                    models_pb2.PaymentType.DESCRIPTOR,
                    company.payment_type,
                ),
                "paymentMethod": protobuf.enum_value_to_slug(
                    models_pb2.PaymentMethod.DESCRIPTOR,
                    company.payment_method,
                ),
                "references": list(company.references),
                "companyType": protobuf.enum_value_to_slug(
                    enum_descriptor=models_pb2.Company.Type.DESCRIPTOR,
                    enum_value=company.company_type,
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


class LeadCompany(models.Resource):
    api_type: ClassVar[str] = "lead-companies"

    @classmethod
    def from_proto(
        cls,
        lead_company: models_pb2.LeadCompany,
        request: requests.Request,
    ) -> LeadCompany:
        return cls(
            id=lead_company.id,
            type=LeadCompany.api_type,
            attributes={
                "name": lead_company.name,
                "salesMarkups": [
                    Money.from_proto(reseller_markup)
                    for reseller_markup in lead_company.sales_markups
                ],
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "LeadCompany",
                        leadCompanyId=lead_company.id,
                    ),
                ),
            },
        )


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


class Transaction(models.Resource):
    api_type: ClassVar[str] = "transactions"

    @classmethod
    def from_proto(
        cls,
        transaction: transaction_models.Transaction,
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
                    models_pb2.PaymentType.DESCRIPTOR,
                    transaction.payment_type,
                ),
                "paymentMethod": protobuf.enum_value_to_slug(
                    models_pb2.PaymentMethod.DESCRIPTOR,
                    transaction.payment_method,
                ),
            },
            relationships={
                "conversion": (
                    {
                        "data": {
                            "id": transaction.conversion_id,
                            "type": "conversions",
                        },
                    }
                    if transaction.conversion_id
                    else None
                ),
                "payer": {
                    "data": {
                        "id": transaction.payer_id,
                        "type": "companies",
                    },
                },
                "beneficiary": {
                    "data": {
                        "id": transaction.beneficiary_id,
                        "type": "companies",
                    },
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


class ContactResource(models.Resource):
    api_type: ClassVar[str] = "contacts"

    @classmethod
    def from_proto(
        cls,
        contact: models_pb2.Contact,
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
                    "data": {
                        "id": contact.company_id,
                        "type": "companies",
                    },
                },
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
                    "data": {
                        "id": balance.account_id,
                        "type": "accounts",
                    },
                },
                "currency": {
                    "data": {
                        "id": balance.currency,
                        "type": "currencies",
                    },
                },
            },
        )


class AccountResource(models.Resource):
    api_type: ClassVar[str] = "accounts"

    @classmethod
    def from_proto(
        cls,
        account: models_pb2.Account,
        request: requests.Request,
    ) -> AccountResource:
        relationships: dict[str, Any] = {
            "company": None,
            "contact": None,
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
                    models_pb2.Status.DESCRIPTOR,
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


class ConversionResource(models.Resource):
    api_type: ClassVar[str] = "conversions"

    @classmethod
    def from_proto(
        cls,
        conversion: Conversion,
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


class CurrenciesResource(models.Resource):
    api_type: ClassVar[str] = "currencies"

    @classmethod
    def from_model(
        cls,
        currency: CurrencyModel,
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


class BeneficiariesResource(models.Resource):
    api_type: ClassVar[str] = "beneficiaries"

    @classmethod
    def from_models(
        cls,
        beneficiary: models_pb2.Beneficiary,
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
                    "data": {
                        "id": beneficiary.account_id,
                        "type": "accounts",
                    },
                },
                "currency": {
                    "data": {
                        "id": beneficiary.currency,
                        "type": "currencies",
                    },
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


class PaymentsResource(models.Resource):
    api_type: ClassVar[str] = "payments"

    @classmethod
    def from_models(
        cls,
        payment: Payment,
        request: requests.Request,
    ) -> PaymentsResource:
        return cls(
            id=payment.id,
            type=PaymentsResource.api_type,
            attributes={
                "amount": Money.from_proto(payment.amount).amount,
                "reason": payment.reason,
                "reference": payment.reference,
                "paymentAt": protobuf.protobuf_to_date(
                    payment.payment_due_date,
                ),
                "status": protobuf.enum_value_to_slug(
                    payment_models.Status.DESCRIPTOR,
                    payment.status,
                ),
            },
            relationships={
                "beneficiary": {
                    "data": {
                        "id": payment.beneficiary_id,
                        "type": "beneficiaries",
                    },
                },
                "transaction": {
                    "data": [
                        {"id": transaction_id, "type": "transactions"}
                        for transaction_id in payment.transactions
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Payment",
                        paymentId=payment.id,
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
                    "data": {
                        "id": refund.transaction_id,
                        "type": "transactions",
                    },
                },
                "conversion": (
                    {
                        "data": {
                            "id": refund.conversion_id,
                            "type": "conversions",
                        },
                    }
                    if refund.conversion_id
                    else None
                ),
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
