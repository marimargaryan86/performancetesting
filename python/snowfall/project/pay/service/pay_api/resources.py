from __future__ import annotations

from typing import Any, ClassVar

from starlette import requests

from snowfall.project.pay.service.accounts.v1alpha import models_pb2 as account_models
from snowfall.project.pay.service.beneficiaries.v1alpha import (
    models_pb2 as beneficiary_models,
)
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
from snowfall.vendor.currency_cloud.models import beneficiary as beneficiary_cc_models

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
            attributes={
                "amount": money.from_protobuf(quotation.amounts.quotation).amount,
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
        relationships = (
            {
                "account": {
                    "data": {
                        "id": company.account_id,
                        "type": "accounts",
                    },
                },
            }
            if company.account_id
            else {}
        )

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
    def from_proto(
        cls,
        account: account_models.Account,
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
                "status": account.status,
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
            attributes={
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
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Conversion",
                        conversionId=conversion.id,
                    ),
                ),
            },
        )
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


class BeneficiariesResource(models.Resource):
    api_type: ClassVar[str] = "beneficiaries"

    @classmethod
    def from_models(
        cls,
        beneficiary: beneficiary_models.Beneficiary,
        cc_beneficiary: beneficiary_cc_models.BeneficiaryResponse,
        request: requests.Request,
    ) -> BeneficiariesResource:
        return cls(
            id=beneficiary.id,
            type=BeneficiariesResource.api_type,
            attributes={
                "bankAccountHolderName": cc_beneficiary.bank_account_holder_name,
                "email": cc_beneficiary.email,
                "beneficiaryAddress": {
                    "addressLines": cc_beneficiary.beneficiary_address,
                    "countryCode": cc_beneficiary.beneficiary_country,
                    "postalCode": cc_beneficiary.beneficiary_postcode or "",
                    "city": cc_beneficiary.beneficiary_city,
                    "state": cc_beneficiary.beneficiary_state_or_province,
                },
                "bankDetails": {
                    **(
                        {
                            "accountNumber": cc_beneficiary.account_number,
                            "aba": cc_beneficiary.routing_code_value_1,
                        }
                        if cc_beneficiary.account_number
                        else {
                            "iban": cc_beneficiary.iban,
                        }
                    ),
                    "name": cc_beneficiary.bank_name,
                    "bicSwift": cc_beneficiary.bic_swift,
                    "accountType": cc_beneficiary.bank_account_type,
                    "paymentTypes": (
                        cc_beneficiary.payment_types and cc_beneficiary.payment_types[0]
                    ),
                    "address": {
                        "addressLines": cc_beneficiary.bank_address,
                        "countryCode": cc_beneficiary.bank_country,
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
                        "id": cc_beneficiary.currency,
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
