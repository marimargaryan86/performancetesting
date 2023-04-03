from typing import Literal

from pydantic.fields import Field
from pydantic.main import BaseModel


class PayBaseModel(BaseModel):
    class Config(object):
        allow_population_by_field_name = True


class PayQuoteAttributes(PayBaseModel):
    amount: int
    external_reference: str | None = Field(alias="externalReference", default=None)


class PayQuoteCompanyData(PayBaseModel):
    id: str  # noqa:A003
    type: Literal["companies"] = "companies"  # noqa:A003


class PayQuoteCompany(PayBaseModel):
    data: PayQuoteCompanyData  # noqa:WPS110


class PayQuoteCurrencyData(PayBaseModel):
    id: str  # noqa:A003
    type: Literal["currencies"] = "currencies"  # noqa:A003


class PayQuoteCurrency(PayBaseModel):
    data: PayQuoteCurrencyData  # noqa:WPS110


class PayQuoteRelationships(PayBaseModel):
    from_currency: PayQuoteCurrency = Field(alias="fromCurrency")
    to_currency: PayQuoteCurrency = Field(alias="toCurrency")
    beneficiary: PayQuoteCompany
    payer: PayQuoteCompany


class PayQuoteData(PayBaseModel):
    type: Literal["quotes"] = "quotes"  # noqa:A003
    attributes: PayQuoteAttributes
    relationships: PayQuoteRelationships


class PayQuoteRequest(PayBaseModel):
    data: PayQuoteData  # noqa:WPS110


class PayQuoteResponse(PayBaseModel):
    id: str  # noqa:A003
    data: PayQuoteData  # noqa:WPS110
