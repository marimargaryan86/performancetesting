from collections.abc import Sequence
from typing import ClassVar, Self

from pydantic import types
from starlette import requests, responses, status

from snowfall.project.junction.rocket.service.api import models as api_models
from snowfall.project.junction.rocket.service.api.places.models import places
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models as std_models


class _Passenger(api_models.BaseModel):
    date_of_birth: types.PastDate


class SuggestionSearchBody(api_models.BaseModel):
    origin: str
    destination: str
    departure_after: types.FutureDatetime
    passengers: list[_Passenger]


class ValidationError(Exception):
    def __init__(self, errors: Sequence[std_models.Error]) -> None:
        self._errors = errors

    def to_response(self) -> responses.Response:
        return std_models.JsonApiResponse(
            body=std_models.Body(errors=self._errors),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class SuggestionSearch(std_models.Resource):
    api_type: ClassVar[str] = "journey-suggestion-searches"

    @classmethod
    def from_proto(
        cls,
        proto: multi_modal_pb2.SuggestionSearch,
        request: requests.Request,
    ) -> Self:
        return cls(
            id=proto.id,
            type=SuggestionSearch.api_type,
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
                "origin": {
                    "data": std_models.ResourceIdentifier(
                        id=proto.criteria.origin_id,
                        type=places.PlacesResource.api_type,
                    ),
                },
                "destination": {
                    "data": std_models.ResourceIdentifier(
                        id=proto.criteria.destination_id,
                        type=places.PlacesResource.api_type,
                    ),
                },
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
