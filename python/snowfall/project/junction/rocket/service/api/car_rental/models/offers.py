from __future__ import annotations

import typing

from snowfall.project.junction.rocket.service.api.common import models as common_models
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import models


class OfferResource(models.Resource):
    api_type: typing.ClassVar[str] = "car-rental-offers"

    @classmethod
    def from_proto(cls, offer: models_pb2.Offer) -> OfferResource:
        return cls(
            id=offer.id,
            type=OfferResource.api_type,
            attributes={
                "price": common_models.Price.from_proto(offer.price),
                "priceBreakdown": [
                    common_models.PriceBreakdown.from_proto(price_breakdown)
                    for price_breakdown in offer.price_breakdown
                ],
                "conditionalPrices": [
                    common_models.ConditionalPrice.from_proto(conditional_price)
                    for conditional_price in offer.car_rental.conditional_prices
                ],
            },
        )
