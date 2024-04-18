from __future__ import annotations

import typing

import pydantic
from starlette import requests

from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import amqp_pb2, money_pb2

_SELF_HREF: typing.Literal["self"] = "self"


class FerrySearchResource(models.Resource):
    api_type: typing.ClassVar[str] = "ferry-searches"

    @classmethod
    def from_proto(
        cls,
        search: models_pb2.Search,
        request: requests.Request,
    ) -> FerrySearchResource:
        res = cls(
            id=search.id,
            type=FerrySearchResource.api_type,
            attributes={
                "origin": {
                    "latitude": search.ferry.origin.coordinates.latitude,
                    "longitude": search.ferry.origin.coordinates.longitude,
                },
                "destination": {
                    "latitude": search.ferry.destination.coordinates.latitude,
                    "longitude": search.ferry.destination.coordinates.longitude,
                },
                "departureAfter": protobuf.protobuf_to_datetime(
                    search.ferry.departure_after,
                ),
                "status": protobuf.enum_value_to_slug(
                    amqp_pb2.Trackable.Status.DESCRIPTOR,
                    search.status,
                ),
                "expiresAt": protobuf.protobuf_to_datetime(search.expires_at),
                "passengers": [
                    {"dateOfBirth": protobuf.protobuf_to_date(passenger.date_of_birth)}
                    for passenger in search.ferry.passengers
                ],
                "vehicles": [
                    {
                        "vehicleType": protobuf.enum_value_to_slug(
                            models_pb2.Vehicle.TypeId.DESCRIPTOR,
                            vehicle.type_id,
                        ),
                    }
                    for vehicle in search.ferry.vehicles
                ],
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewFerrySearch",
                        searchId=search.id,
                    ),
                ),
            },
        )

        if search.ferry.HasField("return_date"):
            res.attributes["returnAt"] = protobuf.protobuf_to_datetime(  # type: ignore[index]
                search.ferry.return_date,
            )

        if search.ferry.outbound_offer_id:
            res.relationships = {
                "selectedOutboundOffer": {
                    "data": (
                        models.ResourceIdentifier(
                            id=search.ferry.outbound_offer_id,
                            type=OfferResource.api_type,
                        )
                    ),
                },
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


class OfferResource(models.Resource):
    api_type: typing.ClassVar[str] = "ferry-offers"

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
            },
            relationships={
                "resultDetails": {
                    "data": models.ResourceIdentifier(
                        id=offer.ferry.ferry_result_detail_id,
                        type=ResultDetailResource.api_type,
                    ),
                },
            },
        )


class ResultDetailResource(models.Resource):
    api_type: typing.ClassVar[str] = "ferry-result-details"

    @classmethod
    def from_proto(cls, result_detail: models_pb2.ResultDetail) -> ResultDetailResource:
        return cls(
            id=result_detail.id,
            type=ResultDetailResource.api_type,
            attributes={
                "origin": {
                    "latitude": result_detail.ferry.origin.coordinates.latitude,
                    "longitude": result_detail.ferry.origin.coordinates.longitude,
                },
                "destination": {
                    "latitude": result_detail.ferry.destination.coordinates.latitude,
                    "longitude": result_detail.ferry.destination.coordinates.longitude,
                },
                "departureAt": protobuf.protobuf_to_datetime(
                    result_detail.ferry.departure_date,
                ),
                "arrivalAt": protobuf.protobuf_to_datetime(
                    result_detail.ferry.arrival_date,
                ),
                "outboundSegment": result_detail.ferry.outbound_segment,
                "segmentSequence": result_detail.ferry.segment_sequence,
                "duration": result_detail.ferry.duration_in_minutes,
                "ferryOperator": {"name": result_detail.ferry.ferry_operator.name},
            },
        )


class SearchResultResource(models.Resource):
    api_type: typing.ClassVar[str] = "ferry-search-results"

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
                        type=FerrySearchResource.api_type,
                    ),
                },
            },
        )
