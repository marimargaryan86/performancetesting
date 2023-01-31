from __future__ import annotations

from typing import ClassVar

from starlette import requests

from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.project.pay.service.quotations.v1alpha import (
    models_pb2 as quotation_models,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transaction_models,
)
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models


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
            },
            relationships={
                "quotation": {
                    "data": {
                        "id": transaction.quotation_id,
                        "type": "quotations",
                    },
                },
            },
        )
