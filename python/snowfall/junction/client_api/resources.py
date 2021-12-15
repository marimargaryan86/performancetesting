from __future__ import annotations

from starlette import requests

from snowfall.adapter import places
from snowfall.junction.client_api import models


class PlaceResource(models.Resource):
    @classmethod
    async def from_data_class(
        cls,
        place: places.Place,
        request: requests.Request,
    ) -> PlaceResource:
        return cls(
            id=str(place.identifier),
            type="places",
            attributes={},
            links={
                "self": request.url_for(
                    "ViewPlace",
                    placeId=place.identifier,
                ),
            },
        )
