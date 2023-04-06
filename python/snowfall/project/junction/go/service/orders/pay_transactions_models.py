from typing import Literal

from pydantic.fields import Field
from pydantic.main import BaseModel


class PayBaseModel(BaseModel):
    class Config(object):
        allow_population_by_field_name = True


class PayTransactionMoney(PayBaseModel):
    currency: str
    amount: int


class PayTransactionAmounts(PayBaseModel):
    beneficiary: PayTransactionMoney
    quotation: PayTransactionMoney
    base_converted: PayTransactionMoney = Field(alias="baseConverted")
    sales_margin: PayTransactionMoney = Field(alias="salesMargin")
    fx_margin: PayTransactionMoney = Field(alias="fxMargin")
    fx_provider_margin: PayTransactionMoney = Field(alias="fxProviderMargin")


class PayTransactionRates(PayBaseModel):
    fx_quote: float = Field(alias="fxQuote")
    fx_buffer: float = Field(alias="fxBuffer")
    sales_markup: float = Field(alias="salesMarkup")
    fx_markup: float = Field(alias="fxMarkup")


class PayTransactionAttributes(PayBaseModel):
    external_reference: str = Field(alias="externalReference")
    parent_external_reference: str = Field(alias="parentExternalReference")
    created_at: str = Field(alias="createdAt")
    amounts: PayTransactionAmounts
    rates: PayTransactionRates


class PayTransactionConversionData(PayBaseModel):
    id: str  # noqa:A003
    type: Literal["conversions"] = "conversions"  # noqa:A003


class PayTransactionConversion(PayBaseModel):
    data: PayTransactionConversionData  # noqa:WPS110


class PayTransactionCompanyData(PayBaseModel):
    id: str  # noqa:A003
    type: Literal["companies"] = "companies"  # noqa:A003


class PayTransactionCompany(PayBaseModel):
    data: PayTransactionCompanyData  # noqa:WPS110


class PayTransactionRelationships(PayBaseModel):
    conversion: PayTransactionConversion
    payer: PayTransactionCompany
    beneficiary: PayTransactionCompany


class PayTransactionData(PayBaseModel):
    id: str  # noqa:A003
    type: Literal["transactions"] = "transactions"  # noqa:A003
    attributes: PayTransactionAttributes
    relationships: PayTransactionRelationships


class PayTransactionResponse(PayBaseModel):
    data: PayTransactionData  # noqa:WPS110
