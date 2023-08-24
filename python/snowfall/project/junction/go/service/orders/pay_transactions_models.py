from typing import Literal

from pydantic.v1.fields import Field
from pydantic.v1.main import BaseModel


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
    processing_margin: PayTransactionMoney = Field(alias="processingMargin")


class PayTransactionRates(PayBaseModel):
    fx_quote: float = Field(alias="fxQuote")
    fx_buffer: float = Field(alias="fxBuffer")
    sales_markup: float = Field(alias="salesMarkup")
    fx_markup: float = Field(alias="fxMarkup")
    processing_markup: float = Field(alias="processingMarkup")


class PayTransactionAttributes(PayBaseModel):
    external_reference: str = Field(alias="externalReference")
    invoice_reference: str = Field(alias="invoiceReference")
    created_at: str = Field(alias="createdAt")
    amounts: PayTransactionAmounts
    rates: PayTransactionRates


class PayTransactionConversionData(PayBaseModel):
    id: str  # noqa: A003
    type: Literal["conversions"] = "conversions"  # noqa: A003


class PayTransactionConversion(PayBaseModel):
    data: PayTransactionConversionData  # noqa: WPS110


class PayTransactionCompanyData(PayBaseModel):
    id: str  # noqa: A003
    type: Literal["companies"] = "companies"  # noqa: A003


class PayTransactionCompany(PayBaseModel):
    data: PayTransactionCompanyData  # noqa: WPS110


class PayTransactionRelationships(PayBaseModel):
    conversion: PayTransactionConversion
    payer: PayTransactionCompany
    beneficiary: PayTransactionCompany


class PayTransactionData(PayBaseModel):
    id: str  # noqa: A003
    type: Literal["transactions"] = "transactions"  # noqa: A003
    attributes: PayTransactionAttributes
    relationships: PayTransactionRelationships


class PayTransactionResponse(PayBaseModel):
    data: PayTransactionData  # noqa: WPS110
