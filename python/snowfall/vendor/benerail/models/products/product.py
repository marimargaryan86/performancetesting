import datetime
from typing import Literal

import pydantic

from snowfall.vendor.benerail.enums import ServiceClassType
from snowfall.vendor.benerail.models.base import BenerailBaseModel


class ConditionAfterSalesFee(BenerailBaseModel):
    fee_price: int | None
    is_allocator_fee: bool | None


class ComfortClass(BenerailBaseModel):
    href: str | None
    comfort_class_value: str | None = pydantic.Field(..., alias="value")


class Condition(BenerailBaseModel):
    condition_type: Literal["SALE", "EXCHANGE", "REFUND", "TRAVEL"] = pydantic.Field(
        ...,
        alias="type",
    )
    description: str
    valid_from: datetime.datetime | None
    valid_until: datetime.datetime | None
    after_sales_free: ConditionAfterSalesFee | None


class ServiceClass(BenerailBaseModel):
    service_class_type: ServiceClassType | None = pydantic.Field(
        ...,
        alias="type",
    )
    name: str | None


class Product(BenerailBaseModel):
    identifier: str | None = pydantic.Field(..., alias="id")
    abstract: str | None
    code: str | None
    description: str | None
    conditions: list[Condition] | None
    service_class: ServiceClass | None
    comfort_class: ComfortClass | None
    is_train_bound: bool | None
    is_return_product: bool | None
