from __future__ import annotations

import typing

from starlette import requests

from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import amqp_pb2

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
                "returnAt": protobuf.protobuf_to_datetime(search.ferry.return_date),
                "status": protobuf.enum_value_to_slug(
                    amqp_pb2.Trackable.Status.DESCRIPTOR,
                    search.status,
                ),
                "expiresAt": protobuf.protobuf_to_datetime(search.expires_at),
                "passengers": [
                    {"dateOfBirth": protobuf.protobuf_to_date(passenger.date_of_birth)}
                    for passenger in search.ferry.passengers
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
                        type=FerrySearchResource.api_type,
                    ),
                },
            },
        )
