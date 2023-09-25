import datetime
from collections.abc import Sequence
from decimal import Decimal

from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.transactions.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format.protobuf import datetime_to_protobuf
from snowfall.stdlib.v1 import money_pb2

_EXPIRATION_MINUTES = 15


class Quote(object):
    def __init__(  # noqa: WPS211
        self,
        amount: int,
        from_currency: money.Currency,
        to_currency: money.Currency,
        rate: float,
        company: company_models.Company,
        beneficiary_id: str,
        tax: int,
    ) -> None:
        self._amount = amount
        self._from_currency = from_currency
        self._to_currency = to_currency
        self._rate = rate
        self._company = company
        self._reseller_markup = self._get_markup(
            getattr(self._company, "reseller_markups", []),
        )
        self._tax = money.Money(tax, currency=self._from_currency)
        self._quotation_amounts = self._calculate_margins()
        self._beneficiary_id = beneficiary_id

    def to_proto(
        self,
    ) -> models_pb2.Quotation:
        return models_pb2.Quotation(
            id=string.uuid(),
            status=models_pb2.QuotationStatus.QUOTATION_STATUS_QUOTED,
            amounts=models_pb2.QuotationAmounts(
                beneficiary=self._quotation_amounts["beneficiary"].protobuf(),
                base_converted=self._quotation_amounts["base_converted"].protobuf(),
                sales_margin=self._quotation_amounts["sales_margin"].protobuf(),
                quotation=self._quotation_amounts["quotation"].protobuf(),
                fx_margin=self._quotation_amounts["fx_margin"].protobuf(),
                processing_margin=self._quotation_amounts[
                    "processing_margin"
                ].protobuf(),
                tax_converted=self._quotation_amounts["tax_converted"].protobuf(),
                total_markups=self._quotation_amounts["total_markups"].protobuf(),
                service_markup=self._quotation_amounts["service_markup"].protobuf(),
                total_amount=self._quotation_amounts["total_amount"].protobuf(),
                reseller_markup=self._reseller_markup.protobuf(),
                tax=self._tax.protobuf(),
            ),
            rates=models_pb2.QuotationRates(
                fx_quote=self._rate,
                fx_buffer=self._calculate_fx_buffer_rate(self._company.fx_markup),
                fx_markup=self._company.fx_markup,
                sales_markup=self._company.sales_markup,
                processing_markup=self._company.processing_markup,
            ),
            expires_at=datetime_to_protobuf(self._calculate_expires_at()),
            payer_id=self._company.id,
            beneficiary_id=self._beneficiary_id,
        )

    def _calculate_expires_at(self) -> datetime.datetime:
        return datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
            minutes=_EXPIRATION_MINUTES,
        )

    def _calculate_fx_buffer_rate(self, buffer_rate: float) -> float:
        return self._rate * buffer_rate / 100

    def _calculate_margins(self) -> dict[str, money.Money]:  # noqa: WPS210, WPS204
        beneficiary = money.Money(self._amount, currency=self._from_currency)
        rate = Decimal(self._rate)
        base_converted = beneficiary.convert(
            self._to_currency,
            rate,
        )
        sales_margin = base_converted.convert(
            self._to_currency,
            Decimal(self._company.sales_markup / 100),
        )
        tax_converted = self._tax.convert(
            self._to_currency,
            rate,
        )

        if self._from_currency == self._to_currency:
            fx_margin = money.Money(0, self._to_currency)
            processing_margin = money.Money(0, self._to_currency)
        else:
            fx_margin = base_converted.convert(
                self._to_currency,
                Decimal(self._company.fx_markup / 100),
            )
            processing_margin = base_converted.convert(
                self._to_currency,
                Decimal(self._company.processing_markup / 100),
            )

        service_markup = money.total(
            [
                fx_margin,
                processing_margin,
                sales_margin,
            ],
        )

        total_markups = money.total(
            [
                service_markup,
                self._reseller_markup.convert(self._to_currency, rate),
            ],
        )

        return {
            "beneficiary": beneficiary,
            "base_converted": base_converted,
            "sales_margin": sales_margin,
            "fx_margin": fx_margin,
            "processing_margin": processing_margin,
            "tax_converted": tax_converted,
            "total_markups": total_markups,
            "service_markup": service_markup,
            "total_amount": money.total(
                [
                    base_converted,
                    total_markups,
                    tax_converted,
                    self._reseller_markup.convert(
                        self._to_currency,
                        rate,
                    ),
                ],
            ),
            "quotation": money.total(
                [
                    base_converted,
                    fx_margin,
                    processing_margin,
                    sales_margin,
                ],
            ),
        }

    def _get_markup(self, markups: Sequence[money_pb2.Money]) -> money.Money:
        for proto_markup in markups:
            markup = money.from_protobuf(proto_markup)
            if markup.currency == self._to_currency:
                return markup
        return money.Money(0, self._to_currency)
