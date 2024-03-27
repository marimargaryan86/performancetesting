from __future__ import annotations

import typing

from starlette import requests

from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import amqp_pb2

_SELF_HREF: typing.Literal["self"] = "self"


class CarSearchResource(models.Resource):
    api_type: typing.ClassVar[str] = "car-searches"

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
                "pickupLocation": {
                    "latitude": search.car_rental.origin.coordinates.latitude,
                    "longitude": search.car_rental.origin.coordinates.longitude,
                },
                "returnLocation": {
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


class OfferResource(models.Resource):
    api_type: typing.ClassVar[str] = "offers"


class ResultDetailResource(models.Resource):
    api_type: typing.ClassVar[str] = "result-details"


class SearchResultResource(models.Resource):
    api_type: typing.ClassVar[str] = "search-results"

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
