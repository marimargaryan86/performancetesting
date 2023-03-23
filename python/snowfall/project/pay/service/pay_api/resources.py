from __future__ import annotations

from typing import ClassVar

from starlette import requests

from snowfall.project.pay.service.accounts.v1alpha import models_pb2 as account_models
from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.project.pay.service.conversions.v1alpha.models_pb2 import Conversion
from snowfall.project.pay.service.quotations.v1alpha import (
    models_pb2 as quotation_models,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transaction_models,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1alpha import money_pb2
from snowfall.vendor.currency_cloud.models import balance as balance_models

_SELF_HREF = "self"


class QuoteResource(models.Resource):
    api_type: ClassVar[str] = "quotes"

    @classmethod
    def from_proto(
        cls,
        quotation: quotation_models.Quotation,
        request: requests.Request,
    ) -> QuoteResource:
        return cls(
            id=quotation.id,
            type=QuoteResource.api_type,
            attributes={"amount": money.from_protobuf(quotation.offer_amount).amount},
            relationships={
                "fromCurrency": {
                    "data": {
                        "id": quotation.beneficiary_amount.currency_code,
                        "type": "currencies",
                    },
                },
                "toCurrency": {
                    "data": {
                        "id": quotation.offer_amount.currency_code,
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
                "bufferRate": round(company.buffer_rate, 3),
                "salesRate": round(company.sales_rate, 3),
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
    ) -> Transaction:
        return cls(
            id=transaction.id,
            type=Transaction.api_type,
            attributes={
                "externalReference": transaction.external_reference_id,
                "parentExternalReference": transaction.parent_external_id,
                "createdAt": protobuf.protobuf_to_datetime(transaction.created_at),
                "beneficiaryAmount": Money.from_proto(
                    transaction.beneficiary_amount,
                ),
                "offerAmount": Money.from_proto(transaction.offer_amount),
                "convertedBeneficiaryAmount": Money.from_proto(
                    transaction.converted_beneficiary_amount,
                ),
                "bufferAmount": Money.from_proto(transaction.buffer_amount),
                "salesAmount": Money.from_proto(transaction.sales_amount),
                "exchangeRate": round(transaction.exchange_rate, 3),
                "bufferRate": round(transaction.buffer_rate, 3),
                "salesRate": round(transaction.sales_rate, 3),
            },
            relationships={
                "conversion": {
                    "data": {
                        "id": transaction.conversion_id,
                        "type": "conversions",
                    },
                },
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
        )


class ContactResource(models.Resource):
    api_type: ClassVar[str] = "contacts"

    @classmethod
    def from_proto(
        cls,
        contact: account_models.Contact,
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
    def from_values(  # noqa: WPS211
        cls,
        identifier: str,
        name: str,
        status: str,
        company_id: str,
        contact_id: str,
    ) -> AccountResource:
        return cls(
            id=identifier,
            type=AccountResource.api_type,
            attributes={
                "name": name,
                "status": status,
            },
            relationships={
                "company": {
                    "data": {
                        "id": company_id,
                        "type": "companies",
                    },
                },
                "contact": {
                    "data": {
                        "id": contact_id,
                        "type": "contacts",
                    },
                },
            },
        )


class ConversionResource(models.Resource):
    api_type: ClassVar[str] = "conversions"

    @classmethod
    def from_proto(
        cls,
        conversion: Conversion,
    ) -> ConversionResource:
        return cls(
            id=conversion.id,
            type=ConversionResource.api_type,
            attributes={
                "settledAt": protobuf.protobuf_to_datetime(
                    conversion.settlement_date,
                ),
                "rate": round(conversion.core_rate, 3),
            },
        )


class CurrenciesResource(models.Resource):
    api_type: ClassVar[str] = "currencies"

    @classmethod
    def from_model(
        cls,
        currency: money.Currency,
        request: requests.Request,
    ) -> CurrenciesResource:
        return cls(
            id=currency.code,
            type=CurrenciesResource.api_type,
            attributes={
                "name": currency.currency_name,
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
