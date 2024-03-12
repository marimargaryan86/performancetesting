from __future__ import annotations

from typing import ClassVar, Literal

from starlette import requests

from snowfall.project.pay.service.companies.v1 import models_pb2
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transaction_models,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import money_pb2

_SELF_HREF: Literal["self"] = "self"


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
                "feeAmount": money.from_protobuf(
                    quotation.amounts.fee_amount,
                ).amount,
            },
            relationships={
                "fromCurrency": {
                    "data": models.ResourceIdentifier(
                        id=quotation.amounts.beneficiary.currency_code,
                        type="currencies",
                    ),
                },
                "toCurrency": {
                    "data": models.ResourceIdentifier(
                        id=quotation.amounts.quotation.currency_code,
                        type="currencies",
                    ),
                },
                "payer": {
                    "data": models.ResourceIdentifier(
                        id=quotation.payer_id,
                        type="companies",
                    ),
                },
                "beneficiary": {
                    "data": models.ResourceIdentifier(
                        id=quotation.beneficiary_id,
                        type="companies",
                    ),
                },
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
