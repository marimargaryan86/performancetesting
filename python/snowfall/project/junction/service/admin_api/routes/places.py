from typing import Any, Mapping

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.adapter import locations, places
from snowfall.project.junction.service.admin_api import resources
from snowfall.project.junction.service.admin_api.validators import (
    places as places_validator,
)
from snowfall.project.junction.service.places.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1alpha import latlng_pb2

_place_id_key = "placeId"


def _update_place_from_payload(
    place: models_pb2.Place,
    payload: Mapping[str, Any],
    validation_result: places_validator.ValidationResult,
) -> models_pb2.Place:
    return models_pb2.Place(
        location=models_pb2.Location(
            id=place.location.id,
            country_code=place.location.country_code,
            time_zone=place.location.time_zone,
            name=payload.get("name", place.location.name),
            coordinates=latlng_pb2.LatLng(
                latitude=payload.get(
                    "latitude",
                    place.location.coordinates.latitude,
                ),
                longitude=payload.get(
                    "longitude",
                    place.location.coordinates.longitude,
                ),
            ),
            types=validation_result.types or place.location.types,  # type: ignore[arg-type]
        ),
        merged_ids=validation_result.locations or place.merged_ids,
    )


class Place(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        place = await client.get(request.path_params[_place_id_key])

        return await messages.create_response(
            body=models.Body(
                data=resources.PlaceResource.from_proto(place, request),
            ),
            request=request,
        )

    async def delete(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        await client.delete(request.path_params[_place_id_key])

        return await messages.create_response(
            body=models.Body(
                data=None,
            ),
            request=request,
            status_code=status.HTTP_204_NO_CONTENT,
        )

    async def patch(  # noqa: WPS217
        self,
        request: requests.Request,
        locations_client: locations.Client = lagom.injectable,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        payload = await request_helpers.flatten_request(request)
        validation_result = await places_validator.validate_relationships(
            locations_client,
            payload,
        )
        place = await client.get(request.path_params[_place_id_key])

        if validation_result.errors:
            return await messages.create_response(
                body=models.Body(errors=list(validation_result.errors)),
                request=request,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        place = await client.update(
            _update_place_from_payload(
                place=place,
                payload=payload,
                validation_result=validation_result,
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.PlaceResource.from_proto(place, request),
            ),
            request=request,
        )


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find(limit=pagination.limit, cursor=pagination.cursor)

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.PlaceResource.from_proto(place, request)
                    for place in response.places
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Places"),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )

    async def post(
        self,
        request: requests.Request,
        locations_client: locations.Client = lagom.injectable,
        places_client: places.Client = lagom.injectable,
    ) -> responses.Response:
        payload = await request_helpers.flatten_request(request)
        validation_result = await places_validator.validate_relationships(
            locations_client,
            payload,
        )

        if validation_result.errors:
            return await messages.create_response(
                body=models.Body(errors=list(validation_result.errors)),
                request=request,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        place = await places_client.create(
            models_pb2.Place(
                location=models_pb2.Location(
                    name=payload["name"],
                    coordinates=latlng_pb2.LatLng(
                        latitude=payload["latitude"],
                        longitude=payload["longitude"],
                    ),
                    types=validation_result.types,  # type: ignore[arg-type]
                ),
                merged_ids=validation_result.locations,
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.PlaceResource.from_proto(place, request),
            ),
            request=request,
            headers={
                "Location": str(
                    request.url_for(
                        "Place",
                        placeId=place.location.id,
                    ),
                ),
            },
            status_code=status.HTTP_201_CREATED,
        )
