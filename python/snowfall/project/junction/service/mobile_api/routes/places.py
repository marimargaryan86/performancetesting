from typing import Sequence

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.service.mobile_api import repository, resources
from snowfall.stdlib.integration.starlette import models

_SEARCH_KEY = "query[name]"


class Place(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        places_repository: repository.PlacesRepository = lagom.injectable,
    ) -> responses.Response:
        place = await places_repository.find_by_id(request.path_params["placeId"])
        if place is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return models.JsonApiResponse(
            models.Body(
                data=resources.PlaceResource.from_proto(place),
            ),
        )


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
                place.attributes.get("countryCode"),
            )
            if place_attributes not in seen_places_attributes:
                deduplicated_places.append(place)
                seen_places_attributes.add(place_attributes)

        return deduplicated_places
