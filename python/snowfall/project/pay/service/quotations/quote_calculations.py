import datetime
from decimal import Decimal

from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.quotations.v1alpha import (
    models_pb2 as quotation_models,
)
from snowfall.stdlib import string
from snowfall.stdlib.format.protobuf import datetime_to_protobuf
from snowfall.stdlib.money import Currency, Money, total

_EXPIRATION_MINUTES = 15


class Quote(object):
    def __init__(  # noqa: WPS211
        self,
        amount: int,
        from_currency: Currency,
        to_currency: Currency,
        rate: float,
        company: company_models.Company,
        beneficiary_id: str,
    ) -> None:
        self._amount = amount
        self._from_currency = from_currency
        self._to_currency = to_currency
        self._rate = rate
        self._company = company
        self._quotation_amounts = self._calculate_margins()
        self._beneficiary_id = beneficiary_id

    def to_proto(
        self,
    ) -> quotation_models.Quotation:
        return quotation_models.Quotation(
            id=string.uuid(),
            status=quotation_models.Quotation.Status.STATUS_QUOTED,
            beneficiary_amount=self._quotation_amounts["initial_amount"].protobuf(),
            exchange_rate=self._rate,
            converted_beneficiary_amount=self._quotation_amounts[
                "converted_amount"
            ].protobuf(),
            buffer_rate=self._company.buffer_rate,
            buffer_amount=self._quotation_amounts["buffer_margin"].protobuf(),
            sales_rate=self._company.sales_rate,
            sales_amount=self._quotation_amounts["sales_margin"].protobuf(),
            offer_amount=self._quotation_amounts["total_amount"].protobuf(),
            expires_at=datetime_to_protobuf(self._calculate_expires_at()),
            payer_id=self._company.id,
            beneficiary_id=self._beneficiary_id,
        )

    def _calculate_expires_at(self) -> datetime.datetime:
        return datetime.datetime.now() + datetime.timedelta(minutes=_EXPIRATION_MINUTES)

    def _calculate_margins(self) -> dict[str, Money]:
        initial_amount = Money(self._amount, currency=self._from_currency)
        converted_amount = initial_amount.convert(
            self._to_currency,
            Decimal(self._rate),
        )
        sales_margin = converted_amount.convert(
            self._to_currency,
            Decimal(self._company.sales_rate),
        )
        if self._from_currency == self._to_currency:
            buffer_margin = Money(0, self._to_currency)
        else:
            buffer_margin = converted_amount.convert(
                self._to_currency,
                Decimal(self._company.buffer_rate),
            )

        return {
            "initial_amount": initial_amount,
            "converted_amount": converted_amount,
            "sales_margin": sales_margin,
            "buffer_margin": buffer_margin,
            "total_amount": total([converted_amount, sales_margin, buffer_margin]),
        }
