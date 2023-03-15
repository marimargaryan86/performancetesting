from __future__ import annotations

from typing import ClassVar

from starlette import requests

from snowfall.project.junction.service.places.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models

_SELF_HREF = "self"
_DATA_KEY = "data"


class PlaceTypeResource(models.Resource):
    api_type: ClassVar[str] = "place-types"

    @classmethod
    def from_proto(
        cls,
        place_type: models_pb2.Location.Type.ValueType,
        request: requests.Request,
    ) -> PlaceTypeResource:
        place_type_id = protobuf.enum_value_to_slug(
            enum_descriptor=models_pb2.Location.Type.DESCRIPTOR,
            enum_value=place_type,
        )
        return cls(
            id=place_type_id,
            type=PlaceTypeResource.api_type,
            attributes={
                "name": place_type_id,
            },
            # @todo: self link
        )


class LocationResource(models.Resource):
    api_type: ClassVar[str] = "locations"

    @classmethod
    def from_proto(
        cls,
        location: models_pb2.Location,
        request: requests.Request,
    ) -> LocationResource:
        return cls(
            id=location.id,
            type=LocationResource.api_type,
            attributes={
                "countryCode": location.country_code or "GB",
                "iataCode": None,
                "latitude": location.coordinates.latitude,
                "longitude": location.coordinates.longitude,
                "name": location.name,
                "timeZone": location.time_zone,
            },
            relationships={
                "types": {
                    _DATA_KEY: [
                        models.ResourceIdentifier(
                            id=protobuf.enum_value_to_slug(
                                enum_descriptor=models_pb2.Location.Type.DESCRIPTOR,
                                enum_value=location_type,
                            ),
                            type=PlaceTypeResource.api_type,
                        )
                        for location_type in location.types
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Location",
                        locationId=location.id,
                    ),
                ),
            },
        )


class PlaceResource(models.Resource):
    api_type: ClassVar[str] = "places"

    @classmethod
    def from_proto(
        cls,
        place: models_pb2.Place,
        request: requests.Request,
    ) -> PlaceResource:
        return cls(
            id=place.location.id,
            type=PlaceResource.api_type,
            attributes={
                "countryCode": place.location.country_code or "GB",
                "iataCode": None,
                "latitude": place.location.coordinates.latitude,
                "longitude": place.location.coordinates.longitude,
                "name": place.location.name,
                "timeZone": place.location.time_zone,
            },
            relationships={
                "locations": {
                    _DATA_KEY: [
                        models.ResourceIdentifier(
                            id=location_id,
                            type=LocationResource.api_type,
                        )
                        for location_id in place.merged_ids
                    ],
                },
                "types": {
                    _DATA_KEY: [
                        models.ResourceIdentifier(
                            id=protobuf.enum_value_to_slug(
                                enum_descriptor=models_pb2.Location.Type.DESCRIPTOR,
                                enum_value=place_type,
                            ),
                            type=PlaceTypeResource.api_type,
                        )
                        for place_type in place.location.types
                    ],
                },
            },
            links={
                _SELF_HREF: str(
                    request.url_for(
                        "Place",
                        placeId=place.location.id,
                    ),
                ),
            },
        )
