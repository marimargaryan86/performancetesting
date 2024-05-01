from __future__ import annotations

import datetime
import types
import typing

import pydantic
from starlette import requests

from snowfall.project.junction.rocket.service.api.common import models as common_models
from snowfall.project.junction.rocket.service.api.flights import models as flight_models
from snowfall.project.junction.rocket.service.api.trains.models import (
    searches as train_models,
)
from snowfall.project.junction.rocket.service.api.v1alpha import pricing_pb2
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    models,
)

_SELF_HREF: typing.Literal["self"] = "self"

_OFFER_TYPE_MAPPING = types.MappingProxyType({
    "rail": train_models.OfferResource.api_type,
    "air": flight_models.OfferResource.api_type,
})


class PenaltyApplicableTo(models.BaseModel):
    date_of_birth_after: datetime.date | None = pydantic.Field(
        alias="dateOfBirthAfter",
    )
    date_of_birth_before: datetime.date | None = pydantic.Field(
        alias="dateOfBirthBefore",
    )

    @classmethod
    def from_proto(
        cls,
        applicable_to: models_pb2.ApplicableTo,
    ) -> PenaltyApplicableTo:
        return cls(
            dateOfBirthAfter=(
                protobuf.protobuf_to_date(
                    applicable_to.date_of_birth_after,
                )
                if applicable_to.date_of_birth_after.ByteSize()
                else None
            ),
            dateOfBirthBefore=(
                protobuf.protobuf_to_date(
                    applicable_to.date_of_birth_before,
                )
                if applicable_to.date_of_birth_before.ByteSize()
                else None
            ),
        )


class Penalty(models.BaseModel):
    applicable_to: PenaltyApplicableTo = pydantic.Field(alias="applicableTo")
    penalty_type: str = pydantic.Field(alias="penaltyType")
    changeable: bool
    refundable: bool
    conditions_apply: bool = pydantic.Field(alias="conditionsApply")
    applicability: str
    price: common_models.Price | None

    @classmethod
    def from_proto(cls, penalty: models_pb2.Penalty) -> Penalty:
        return cls(
            applicableTo=PenaltyApplicableTo.from_proto(penalty.applicable_to),
            penaltyType=protobuf.enum_value_to_slug(
                enum_descriptor=models_pb2.Penalty.Type.DESCRIPTOR,
                enum_value=penalty.penalty_type,
            ),
            changeable=penalty.changeable,
            refundable=penalty.refundable,
            conditionsApply=penalty.conditions_apply,
            applicability=protobuf.enum_value_to_slug(
                enum_descriptor=models_pb2.Penalty.Applicability.DESCRIPTOR,
                enum_value=penalty.applicability,
            ),
            price=(
                common_models.Price.from_proto(penalty.price)
                if penalty.price.ByteSize()
                else None
            ),
        )


class FareRule(models.BaseModel):
    title: str
    body: str

    @classmethod
    def from_proto(
        cls,
        fare_rule: models_pb2.FareRule,
    ) -> FareRule:
        return cls(
            title=fare_rule.title,
            body=fare_rule.body,
        )

    @classmethod
    def from_flight_proto(
        cls,
        fare_rule: pricing_pb2.FareRule,
    ) -> FareRule:
        return cls(
            title=fare_rule.title,
            body=fare_rule.body,
        )


# TODO(justin.k): required_documents: list[str] = pydantic.Field("requiredDocuments")
class QuotedOfferModel(models.BaseModel):
    offer: str
    price: common_models.Price
    price_breakdown: list[common_models.PriceBreakdown] = pydantic.Field(
        alias="priceBreakdown",
    )
    fare_rules: list[FareRule] = pydantic.Field(alias="fareRules")
    penalties: list[Penalty]
    conditional_prices: list[common_models.ConditionalPrice] = pydantic.Field(
        alias="conditionalPrices",
    )
    required: list[str]

    @classmethod
    def from_flight_quote_proto(
        cls,
        quote: pricing_pb2.Quote,
    ) -> QuotedOfferModel:
        return cls(
            offer=quote.offer_id,
            price=common_models.Price.from_proto(quote.quoted_offer.price),
            priceBreakdown=[
                common_models.PriceBreakdown.from_flight_proto(price_breakdown)
                for price_breakdown in quote.quoted_offer.price_breakdown
            ],
            penalties=[],
            fareRules=[
                FareRule.from_flight_proto(fare_rule)
                for fare_rule in quote.quoted_offer.rules
            ],
            conditionalPrices=[],
            required=[],
        )

    @classmethod
    def from_proto(cls, quoted_offer: models_pb2.QuotedOffer) -> QuotedOfferModel:
        return cls(
            offer=quoted_offer.offer_id,
            price=common_models.Price.from_proto(quoted_offer.price),
            priceBreakdown=[
                common_models.PriceBreakdown.from_proto(price_breakdown)
                for price_breakdown in quoted_offer.price_breakdown
            ],
            penalties=[
                Penalty.from_proto(penalty) for penalty in quoted_offer.penalties
            ],
            fareRules=[
                FareRule.from_proto(fare_rule) for fare_rule in quoted_offer.rules
            ],
            conditionalPrices=[
                common_models.ConditionalPrice(
                    price=common_models.Price.from_proto(conditional_price.price),
                    description=conditional_price.description,
                    includedInTotal=conditional_price.included_in_total,
                )
                for conditional_price in quoted_offer.conditional_prices
            ],
            required=[
                protobuf.enum_value_to_slug(
                    enum_descriptor=models_pb2.QuotedOffer.Required.DESCRIPTOR,
                    enum_value=required_document,
                )
                for required_document in quoted_offer.required_documents
            ],
        )


class QuoteResource(models.Resource):
    api_type: typing.ClassVar[str] = "quotes"

    @classmethod
    def from_flight_quote_proto(
        cls,
        quote: pricing_pb2.Quote,
        request: requests.Request,
    ) -> QuoteResource:
        quoted_offers = []
        total_price = None

        if quote.HasField("quoted_offer"):
            quoted_offers.append(QuotedOfferModel.from_flight_quote_proto(quote))

            total_price = common_models.Price.from_proto(
                quote.quoted_offer.price,
            )

        attributes = {
            "status": protobuf.enum_value_to_slug(
                pricing_pb2.Quote.Status.DESCRIPTOR,
                quote.status,
            ),
            "expiresAt": protobuf.protobuf_to_datetime(quote.expires_at),
            "quotedOffers": quoted_offers,
        }

        if total_price:
            attributes["totalPrice"] = total_price

        return cls(
            id=quote.id,
            type=QuoteResource.api_type,
            attributes=attributes,
            relationships={
                "offers": {
                    "data": [
                        models.ResourceIdentifier(
                            id=quote.offer_id,
                            type="flight-offers",
                        ),
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewQuotes",
                        quoteId=quote.id,
                    ),
                ),
            },
        )

    @classmethod
    def from_proto(
        cls,
        quote: models_pb2.Quote,
        request: requests.Request,
    ) -> QuoteResource:
        if len(quote.quoted_offers) < len(quote.offer_ids):
            status = "processing" if quote.quoted_offers else "pending"
            price = None
        else:
            status = "completed"
            price = common_models.Price.from_proto(
                quote.total_price,
            )

        attributes = {
            "status": status,
            "expiresAt": protobuf.protobuf_to_datetime(quote.expires_at),
            "quotedOffers": [
                QuotedOfferModel.from_proto(quoted_offer)
                for quoted_offer in quote.quoted_offers
            ],
        }

        if price:
            attributes["totalPrice"] = price

        return cls(
            id=quote.id,
            type=QuoteResource.api_type,
            attributes=attributes,
            relationships={
                "offers": {
                    "data": [
                        models.ResourceIdentifier(
                            id=offer_id,
                            type=_OFFER_TYPE_MAPPING.get(
                                protobuf.enum_value_to_slug(
                                    models_pb2.VerticalType.DESCRIPTOR,
                                    quote.vertical_type,
                                ),
                                "",
                            ),
                        )
                        for offer_id in quote.offer_ids
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewQuotes",
                        quoteId=quote.id,
                    ),
                ),
            },
        )
