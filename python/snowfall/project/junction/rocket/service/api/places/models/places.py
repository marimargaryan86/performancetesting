from __future__ import annotations

import typing

from starlette import requests

from snowfall.project.junction.rocket.service.places.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models

_SELF_HREF: typing.Literal["self"] = "self"
IATA_PROVIDER_ID = "d29f7e2e-b6e2-4d59-b33d-289aebbed3c0"


class PlacesResource(models.Resource):
    api_type: typing.ClassVar[str] = "places"

    @classmethod
    def from_proto(
        cls,
        place: models_pb2.Place,
        request: requests.Request,
    ) -> PlacesResource:
        iata = None
        air = place.search_capabilities.air
        if air:
            iata = air[IATA_PROVIDER_ID]

        return cls(
            id=place.id,
            type=PlacesResource.api_type,
            attributes={
                "name": place.name,
                "placeType": protobuf.enum_value_to_slug(
                    models_pb2.Type.DESCRIPTOR,
                    place.type,
                ),
                "latitude": place.coordinates.latitude,
                "longitude": place.coordinates.longitude,
                "countryCode": place.country_code,
                "countryName": place.country_name,
                "iataCode": iata,
                "timeZone": place.time_zone,
                "searchCapabilities": {
                    key: bool(getattr(place.search_capabilities, key))
                    for key in iter(["air", "rail", "ferry"])
                },
                "updatedAt": protobuf.protobuf_to_datetime(place.updated_at),
            },
            relationships=cls._get_relationships(place),
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "GetPlace",
                        placeId=place.id,
                    ),
                ),
            },
        )

    @classmethod
    def _get_relationships(
        cls,
        place: models_pb2.Place,
    ) -> typing.Mapping[str, typing.Any]:
        relationships: typing.MutableMapping[str, typing.Any] = {}

        if place.city.id:
            relationships["city"] = {
                "data": models.ResourceIdentifier(
                    id=place.city.id,
                    type=PlacesResource.api_type,
                ),
            }

        if place.contains:
            relationships["contains"] = {
                "data": [
                    models.ResourceIdentifier(
                        id=contain.id,
                        type=PlacesResource.api_type,
                    )
                    for contain in place.contains
                ],
            }

        return relationships
