from __future__ import annotations

import pydantic

from snowfall.project.junction.rocket.service.api.v1alpha import pricing_pb2
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import money_pb2


class Price(models.BaseModel):
    currency: str
    amount: str

    @classmethod
    def from_proto(cls, price: money_pb2.Money) -> Price:
        money_price = money.from_protobuf(price)

        return cls(
            currency=money_price.currency.code,
            amount=str(money_price),
        )


class PriceBreakdown(models.BaseModel):
    price: Price
    breakdown_type: str = pydantic.Field(alias="breakdownType")

    @classmethod
    def from_proto(
        cls,
        price_breakdown: models_pb2.PriceBreakdown,
    ) -> PriceBreakdown:
        return cls(
            price=Price.from_proto(price_breakdown.price),
            breakdownType=protobuf.enum_value_to_slug(
                enum_descriptor=models_pb2.PriceBreakdown.BreakdownType.DESCRIPTOR,
                enum_value=price_breakdown.breakdown_type,
            ),
        )

    @classmethod
    def from_flight_proto(
        cls,
        price_breakdown: pricing_pb2.PriceBreakdown,
    ) -> PriceBreakdown:
        return cls(
            price=Price.from_proto(price_breakdown.price),
            breakdownType=protobuf.enum_value_to_slug(
                enum_descriptor=models_pb2.PriceBreakdown.BreakdownType.DESCRIPTOR,
                enum_value=price_breakdown.breakdown_type,
            ),
        )


class ConditionalPrice(models.BaseModel):
    price: Price
    description: str | None
    included_in_total: bool | None = pydantic.Field(alias="includedInTotal")

    @classmethod
    def from_proto(
        cls,
        conditional_price: models_pb2.ConditionalPrice,
    ) -> ConditionalPrice:
        return cls(
            price=Price.from_proto(conditional_price.price),
            description=conditional_price.description,
            includedInTotal=conditional_price.included_in_total,
        )
