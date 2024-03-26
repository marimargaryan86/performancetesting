from __future__ import annotations

import typing

from starlette import requests

from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models

_SELF_HREF: typing.Literal["self"] = "self"


class CarSearchResource(models.Resource):
    api_type: typing.ClassVar[str] = "car-searches"


class OfferResource(models.Resource):
    api_type: typing.ClassVar[str] = "offers"


class ResultDetailResource(models.Resource):
    api_type: typing.ClassVar[str] = "result-details"


class SearchResultResource(models.Resource):
    api_type: typing.ClassVar[str] = "search-results"

    @classmethod
    def from_proto(
        cls,
        search_result: models_pb2.SearchResult,
        request: requests.Request,
    ) -> SearchResultResource:
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
