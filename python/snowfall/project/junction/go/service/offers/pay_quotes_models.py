from typing import Literal

from pydantic.v1.fields import Field
from pydantic.v1.main import BaseModel


class PayBaseModel(BaseModel):
    class Config(object):
        allow_population_by_field_name = True


class PayQuoteAttributes(PayBaseModel):
    amount: int
    tax: int
    total_amount: int = Field(alias="totalAmount")
    total_markups: int = Field(alias="totalMarkups")
    service_markup: int = Field(alias="serviceMarkup")
    reseller_markup: int = Field(alias="feeAmount")
    external_reference: str | None = Field(alias="externalReference", default=None)


class PayQuoteCompanyData(PayBaseModel):
    id: str  # noqa: A003
    type: Literal["companies"] = "companies"  # noqa: A003


class PayQuoteCompany(PayBaseModel):
    data: PayQuoteCompanyData


class PayQuoteCurrencyData(PayBaseModel):
    id: str  # noqa: A003
    type: Literal["currencies"] = "currencies"  # noqa: A003


class PayQuoteCurrency(PayBaseModel):
    data: PayQuoteCurrencyData


class PayQuoteRelationships(PayBaseModel):
    from_currency: PayQuoteCurrency = Field(alias="fromCurrency")
    to_currency: PayQuoteCurrency = Field(alias="toCurrency")
    beneficiary: PayQuoteCompany
    payer: PayQuoteCompany


class PayQuoteData(PayBaseModel):
    type: Literal["quotes"] = "quotes"  # noqa: A003
    attributes: PayQuoteAttributes
    relationships: PayQuoteRelationships


class PayQuoteResponseData(PayQuoteData):
    id: str  # noqa: A003


class PayQuoteRequest(PayBaseModel):
    data: PayQuoteData


class PayQuoteResponse(PayBaseModel):
    data: PayQuoteResponseData
