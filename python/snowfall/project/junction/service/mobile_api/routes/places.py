from typing import Sequence

import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.service.mobile_api import repository, resources
from snowfall.stdlib.integration.starlette import models

_SEARCH_KEY = "query[name]"


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        places_repository: repository.PlacesRepository = lagom.injectable,
    ) -> responses.Response:
        search_key = request.query_params.get(_SEARCH_KEY)
        if search_key is None:
            places = await places_repository.find()
        else:
            places = await places_repository.match(search_key)

        places_resources = [
            resources.PlaceResource.from_proto(place) async for place in places
        ]

        deduplicated_places = self._deduplicate_places(places_resources)

        return models.JsonApiResponse(
            models.Body(
                data=deduplicated_places,
            ),
        )

    def _deduplicate_places(
        self,
        places: Sequence[resources.PlaceResource],
    ) -> Sequence[resources.PlaceResource]:
        seen_places_attributes = set()
        deduplicated_places = []
        for place in places:
            if not place.attributes:
                continue

            place_attributes = (
                place.attributes.get("name"),
                place.attributes.get("latitude"),
                place.attributes.get("longitude"),
            )
            if place_attributes not in seen_places_attributes:
                deduplicated_places.append(place)
                seen_places_attributes.add(place_attributes)

        return deduplicated_places
