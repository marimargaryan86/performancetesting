from __future__ import annotations

import typing

from starlette import requests

from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import amqp_pb2

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
                "origin": {
                    "latitude": search.rail.origin.coordinates.latitude,
                    "longitude": search.rail.origin.coordinates.longitude,
                },
                "destination": {
                    "latitude": search.rail.destination.coordinates.latitude,
                    "longitude": search.rail.destination.coordinates.longitude,
                },
                "departureAfter": protobuf.protobuf_to_datetime(
                    search.rail.departure_after,
                ),
                "returnAt": protobuf.protobuf_to_datetime(search.rail.return_date),
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

        if search.rail.HasField("departure_before"):
            res.attributes["departureBefore"] = protobuf.protobuf_to_datetime(  # type: ignore[index]
                search.rail.departure_before,
            )

        if search.rail.outbound_offer_id:
            res.relationships = {
                "selectedOutboundOffer": {
                    "data": (
                        models.ResourceIdentifier(
                            id=search.rail.outbound_offer_id,
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
                        type=RailSearchResource.api_type,
                    ),
                },
            },
        )
