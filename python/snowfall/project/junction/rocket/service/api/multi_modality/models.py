from collections.abc import Sequence
from typing import ClassVar, Self

import more_itertools
from pydantic import types
from starlette import requests, responses, status

from snowfall.project.junction.rocket.service.api import models as api_models
from snowfall.project.junction.rocket.service.api.flights import (
    models as flight_models,
)
from snowfall.project.junction.rocket.service.api.places.models import places
from snowfall.project.junction.rocket.service.api.trains.models import (
    searches as train_models,
)
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models as std_models


class _Passenger(api_models.BaseModel):
    date_of_birth: types.PastDate


class SuggestionSearchBody(api_models.BaseModel):
    origin: str
    destination: str
    departure_after: types.FutureDatetime
    passengers: list[_Passenger]
    return_departure_after: types.FutureDatetime | None = None

    def departure_before_return(self) -> bool:
        if not self.return_departure_after:
            return True

        return self.departure_after < self.return_departure_after


class ValidationError(Exception):
    def __init__(self, errors: Sequence[std_models.Error]) -> None:
        self._errors = errors

    def to_response(self) -> responses.Response:
        return std_models.JsonApiResponse(
            body=std_models.Body(errors=self._errors),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class Suggestion(std_models.Resource):
    api_type: ClassVar[str] = "journey-suggestions"

    @classmethod
    def from_proto(
        cls,
        proto: multi_modal_pb2.Suggestion,
        request: requests.Request,
    ) -> Self:
        offers = more_itertools.bucket(proto.offers, lambda offer: offer.segment_type)

        return cls(
            id=proto.id,
            type=cls.api_type,
            attributes={},
            relationships={
                "flightOffers": std_models.Relationship(
                    data=[
                        std_models.ResourceIdentifier(
                            id=flight_offer.id,
                            type=flight_models.OfferResource.api_type,
                        )
                        for flight_offer in offers[segment_type_pb2.SEGMENT_TYPE_FLIGHT]
                    ],
                ),
                "trainOffers": std_models.Relationship(
                    data=[
                        std_models.ResourceIdentifier(
                            id=train_offer.id,
                            type=train_models.OfferResource.api_type,
                        )
                        for train_offer in offers[segment_type_pb2.SEGMENT_TYPE_TRAIN]
                    ],
                ),
                "flightResults": std_models.Relationship(
                    data=[
                        std_models.ResourceIdentifier(
                            id=flight_offer.result_id,
                            type=flight_models.FlightSearchResultResource.api_type,
                        )
                        for flight_offer in offers[segment_type_pb2.SEGMENT_TYPE_FLIGHT]
                    ],
                ),
                "trainResults": std_models.Relationship(
                    data=[
                        std_models.ResourceIdentifier(
                            id=train_offer.result_id,
                            type=train_models.SearchResultResource.api_type,
                        )
                        for train_offer in offers[segment_type_pb2.SEGMENT_TYPE_TRAIN]
                    ],
                ),
            },
            links=std_models.Links(
                self=str(
                    request.url_for(
                        "GetJourneySuggestion",
                        journeySuggestionId=proto.id,
                    ),
                ),
            ),
        )


class SuggestionSearch(std_models.Resource):
    api_type: ClassVar[str] = "journey-suggestion-searches"

    @classmethod
    def from_proto(
        cls,
        proto: multi_modal_pb2.SuggestionSearch,
        suggestions: Sequence[multi_modal_pb2.Suggestion],
        request: requests.Request,
    ) -> Self:
        return cls(
            id=proto.id,
            type=cls.api_type,
            attributes={
                "departureAfter": protobuf.protobuf_to_datetime(
                    proto.criteria.departure_after,
                ),
                "passengers": [
                    {"dateOfBirth": protobuf.protobuf_to_date(passenger.date_of_birth)}
                    for passenger in proto.criteria.passengers
                ],
                "status": protobuf.enum_value_to_slug(
                    enum_descriptor=multi_modal_pb2.SuggestionSearch.Status.DESCRIPTOR,
                    enum_value=proto.status,
                ),
                "expiresAt": protobuf.protobuf_to_datetime(proto.expires_at),
            },
            relationships={
                "origin": std_models.Relationship(
                    data=std_models.ResourceIdentifier(
                        id=proto.criteria.origin_id,
                        type=places.PlacesResource.api_type,
                    ),
                ),
                "destination": std_models.Relationship(
                    data=std_models.ResourceIdentifier(
                        id=proto.criteria.destination_id,
                        type=places.PlacesResource.api_type,
                    ),
                ),
                "suggestions": std_models.Relationship(
                    data=[
                        std_models.ResourceIdentifier(
                            id=suggestion.id,
                            type=Suggestion.api_type,
                        )
                        for suggestion in suggestions
                    ],
                ),
            },
            links=std_models.Links(
                self=str(
                    request.url_for(
                        "GetJourneySuggestionSearch",
                        journeySuggestionSearchId=proto.id,
                    ),
                ),
            ),
        )
