from __future__ import annotations

from starlette import requests

from snowfall.project.junction.service.places.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models

_SELF_HREF = "self"
_DATA_KEY = "data"


class PlaceResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        place: models_pb2.Place,
        request: requests.Request,
    ) -> PlaceResource:
        return cls(
            id=place.location.id,
            type="places",
            attributes={
                "countryCode": place.location.country_code.rjust(2, "X"),
                "iataCode": None,
                "latitude": place.location.coordinates.latitude,
                "longitude": place.location.coordinates.longitude,
                "name": place.location.name,
                "timeZone": place.location.time_zone,
            },
            relationships={
                "types": {
                    _DATA_KEY: [
                        models.ResourceIdentifier(
                            id=protobuf.enum_value_to_slug(
                                descriptor=models_pb2.Location.Type.DESCRIPTOR,
                                enum_value=place_type,
                            ),
                            type="place-types",
                        )
                        for place_type in place.location.types
                    ],
                },
            },
            links={
                _SELF_HREF: request.url_for(
                    "Place",
                    placeId=place.location.id,
                ),
            },
        )
