from __future__ import annotations

import typing

import pydantic
from starlette import requests

from snowfall.project.junction.rocket.service.api.common import models as common_models
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import amqp_pb2

_SELF_HREF: typing.Literal["self"] = "self"


class CarSearchResource(models.Resource):
    api_type: typing.ClassVar[str] = "car-rental-searches"

    @classmethod
    def from_proto(
        cls,
        search: models_pb2.Search,
        request: requests.Request,
    ) -> CarSearchResource:
        return cls(
            id=search.id,
            type=CarSearchResource.api_type,
            attributes={
                "origin": {
                    "latitude": search.car_rental.origin.coordinates.latitude,
                    "longitude": search.car_rental.origin.coordinates.longitude,
                },
                "destination": {
                    "latitude": search.car_rental.destination.coordinates.latitude,
                    "longitude": search.car_rental.destination.coordinates.longitude,
                },
                "pickupAt": protobuf.protobuf_to_datetime(search.car_rental.pickup_at),
                "returnAt": protobuf.protobuf_to_datetime(search.car_rental.return_at),
                "status": protobuf.enum_value_to_slug(
                    amqp_pb2.Trackable.Status.DESCRIPTOR,
                    search.status,
                ),
                "driverAge": search.car_rental.driver_age,
                "expiresAt": protobuf.protobuf_to_datetime(search.expires_at),
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "ViewCarRentalSearch",
                        searchId=search.id,
                    ),
                ),
            },
        )


class ConditionalPrice(models.BaseModel):
    price: common_models.Price
    description: str | None
    included_in_total: bool | None = pydantic.Field(alias="includedInTotal")

    @classmethod
    def from_proto(
        cls,
        conditional_price: models_pb2.ConditionalPrice,
    ) -> ConditionalPrice:
        return cls(
            price=common_models.Price.from_proto(conditional_price.price),
            description=conditional_price.description,
            includedInTotal=conditional_price.included_in_total,
        )


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
                    ConditionalPrice.from_proto(conditional_price)
                    for conditional_price in offer.car_rental.conditional_prices
                ],
            },
        )


class ResultDetailResource(models.Resource):
    api_type: typing.ClassVar[str] = "car-rental-result-details"

    @classmethod
    def from_proto(cls, result_detail: models_pb2.ResultDetail) -> ResultDetailResource:
        return cls(
            id=result_detail.id,
            type=ResultDetailResource.api_type,
            attributes={
                "imageUrl": result_detail.car_rental.image_url or None,
                "model": result_detail.car_rental.model or None,
                "seatsCount": (
                    result_detail.car_rental.seats_count
                    if result_detail.car_rental.HasField("seats_count")
                    else None
                ),
                "doorsCount": (
                    result_detail.car_rental.doors_count
                    if result_detail.car_rental.HasField("doors_count")
                    else None
                ),
                "transmission": result_detail.car_rental.transmission.lower() or None,
                "baggageQuantity": (
                    result_detail.car_rental.baggage_quantity
                    if result_detail.car_rental.HasField("baggage_quantity")
                    else None
                ),
                "vehicleType": result_detail.car_rental.vehicle_type or None,
                "vendor": result_detail.car_rental.vendor_name or None,
                "unlimitedMileage": result_detail.car_rental.unlimited_mileage or None,
                "airConditioning": result_detail.car_rental.air_conditioner or None,
                "pickupAt": protobuf.protobuf_to_datetime(
                    result_detail.car_rental.pickup_at,
                ),
                "returnAt": protobuf.protobuf_to_datetime(
                    result_detail.car_rental.return_at,
                ),
                "origin": {
                    "latitude": result_detail.car_rental.origin.coordinates.latitude,
                    "longitude": result_detail.car_rental.origin.coordinates.longitude,
                },
                "destination": {
                    "latitude": result_detail.car_rental.destination.coordinates.latitude,
                    "longitude": result_detail.car_rental.destination.coordinates.longitude,
                },
            },
        )


class SearchResultResource(models.Resource):
    api_type: typing.ClassVar[str] = "car-rental-search-results"

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
                        type=CarSearchResource.api_type,
                    ),
                },
            },
        )
