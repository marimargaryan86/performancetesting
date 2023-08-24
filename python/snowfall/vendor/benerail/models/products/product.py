from datetime import datetime

from pydantic.v1 import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.products.enums import SaleType, ServiceClassType


class ConditionAfterSalesFee(BenerailBaseModel):
    fee_price: float | None = None
    is_allocator_fee: bool | None = Field(
        default=False,
        description="indicates whether the fee belongs to the allocator",
    )


class ComfortClass(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:bnds:class:1",
    )
    comfort_class_value: ConstrainedStr | None = Field(
        None,
        example="urn:bnds:class:FF",
        alias="value",
        regex="^urn:[a-z]*:class:[1-2]*$",
    )


class Condition(BenerailBaseModel):
    condition_type: SaleType = Field(..., alias="type")
    description: str
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    after_sales_fee: ConditionAfterSalesFee | None = None


class ServiceClass(BenerailBaseModel):
    service_class_type: ServiceClassType | None = Field(None, alias="type")
    name: str | None = Field(
        None,
        description=(
            "The name the carrier itself uses to designate this specific service class."
        ),
    )


class Product(BenerailBaseModel):
    identifier: str | None = Field(
        None,
        description="unique id of this product on this server.",
        alias="id",
    )
    abstract: str | None = Field(None, example="TGV Lyria Loisir 2")
    code: str | None = Field(
        None,
        example="PT00AD",
    )
    description: str | None = Field(
        None,
        description="the textual description of the product",
        example="Loisir Non-flex Adult Fare",
    )
    conditions: list[Condition] | None = Field(
        None,
        description="Structured description of the sales or after-sales conditions.",
    )
    service_class: ServiceClass | None = None
    comfort_class: ComfortClass | None = None
    is_train_bound: bool | None = False
    is_return_product: bool | None = False
