from __future__ import annotations

import typing

import pydantic
from starlette import requests

from snowfall.project.junction.go.v1 import models_pb2 as go_models_pb2
from snowfall.project.junction.rocket.service.api.places.models import places
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import amqp_pb2, money_pb2

_SELF_HREF: typing.Literal["self"] = "self"


class RailSearchResource(models.Resource):
    api_type: typing.ClassVar[str] = "rail-searches"

    @classmethod
    def from_proto(
        cls,
        search: models_pb2.Search,
        request: requests.Request,
    ) -> RailSearchResource:
        res = cls(
            id=search.id,
            type=RailSearchResource.api_type,
            attributes={
                "departureAfter": protobuf.protobuf_to_datetime(
                    search.rail.departure_after,
                ),
                "status": protobuf.enum_value_to_slug(
                    amqp_pb2.Trackable.Status.DESCRIPTOR,
                    search.status,
                ),
                "expiresAt": protobuf.protobuf_to_datetime(search.expires_at),
                "passengers": [
                    {"dateOfBirth": protobuf.protobuf_to_date(passenger.date_of_birth)}
                    for passenger in search.rail.passengers
                ],
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewRailSearch",
                        searchId=search.id,
                    ),
                ),
            },
        )

        if search.rail.HasField("return_date"):
            res.attributes["returnAt"] = protobuf.protobuf_to_datetime(  # type: ignore[index]
                search.rail.return_date,
            )

        if search.rail.HasField("departure_before"):
            res.attributes["departureBefore"] = protobuf.protobuf_to_datetime(  # type: ignore[index]
                search.rail.departure_before,
            )

        res.relationships = {
            "origin": {
                "data": (
                    models.ResourceIdentifier(
                        id=search.rail.origin_id,
                        type=places.PlacesResource.api_type,
                    )
                ),
            },
            "destination": {
                "data": (
                    models.ResourceIdentifier(
                        id=search.rail.destination_id,
                        type=places.PlacesResource.api_type,
                    )
                ),
            },
        }

        if search.rail.outbound_offer_id:
            res.relationships["selectedOutboundOffer"] = {
                "data": (
                    models.ResourceIdentifier(
                        id=search.rail.outbound_offer_id,
                        type=OfferResource.api_type,
                    )
                ),
            }

        return res


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


class CabinDetails(models.BaseModel):
    result_detail: str = pydantic.Field(alias="resultDetail")
    cabin_type: str = pydantic.Field(alias="cabinType")
    marketing_name: str = pydantic.Field(alias="marketingName")

    @classmethod
    def from_proto(
        cls,
        cabin_detail: models_pb2.CabinDetails,
    ) -> CabinDetails:
        return cls(
            resultDetail=cabin_detail.result_id,
            cabinType=protobuf.enum_value_to_slug(
                enum_descriptor=go_models_pb2.CabinClass.Type.DESCRIPTOR,
                enum_value=cabin_detail.cabin_class.type,
            ),
            marketingName=cabin_detail.cabin_class.marketing_name,
        )


class OfferResource(models.Resource):
    api_type: typing.ClassVar[str] = "rail-offers"

    @classmethod
    def from_proto(cls, offer: models_pb2.Offer) -> OfferResource:
        return cls(
            id=offer.id,
            type=OfferResource.api_type,
            attributes={
                "price": Price.from_proto(offer.price),
                "priceBreakdown": [
                    PriceBreakdown.from_proto(price_breakdown)
                    for price_breakdown in offer.price_breakdown
                ],
                "cabinDetails": [
                    CabinDetails.from_proto(cabin_detail)
                    for cabin_detail in offer.rail.cabin_class
                ],
            },
        )


class ResultDetailResource(models.Resource):
    api_type: typing.ClassVar[str] = "rail-result-details"

    @classmethod
    def from_proto(cls, result_detail: models_pb2.ResultDetail) -> ResultDetailResource:
        return cls(
            id=result_detail.id,
            type=ResultDetailResource.api_type,
            attributes={
                "origin": {
                    "latitude": result_detail.rail.origin.coordinates.latitude,
                    "longitude": result_detail.rail.origin.coordinates.longitude,
                },
                "destination": {
                    "latitude": result_detail.rail.destination.coordinates.latitude,
                    "longitude": result_detail.rail.destination.coordinates.longitude,
                },
                "departureAt": protobuf.protobuf_to_datetime(
                    result_detail.rail.departure_date,
                ),
                "arrivalAt": protobuf.protobuf_to_datetime(
                    result_detail.rail.arrival_date,
                ),
                "outboundSegment": result_detail.rail.outbound_segment,
                "segmentSequence": result_detail.rail.segment_sequence,
            },
        )


class SearchResultResource(models.Resource):
    api_type: typing.ClassVar[str] = "rail-search-results"

    @classmethod
    def from_proto(cls, search_result: models_pb2.SearchResult) -> SearchResultResource:
        return cls(
            id=search_result.id,
            type=SearchResultResource.api_type,
            attributes={
                "expiresAt": protobuf.protobuf_to_datetime(search_result.expires_at),
            },
            relationships={
                "offers": {
                    "data": [
                        models.ResourceIdentifier(
                            id=offer.id,
                            type=OfferResource.api_type,
                        )
                        for offer in search_result.offers
                    ],
                },
                "resultDetails": {
                    "data": [
                        models.ResourceIdentifier(
                            id=detail.id,
                            type=ResultDetailResource.api_type,
                        )
                        for detail in search_result.result_details
                    ],
                },
                "search": {
                    "data": models.ResourceIdentifier(
                        id=search_result.search_id,
                        type=RailSearchResource.api_type,
                    ),
                },
            },
        )
