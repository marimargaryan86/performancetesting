import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.adapter import locations
from snowfall.project.junction.service.admin_api import resources
from snowfall.stdlib.integration.starlette import models, pagination_helpers


class Location(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: locations.Client = lagom.injectable,
    ) -> responses.Response:
        location = await client.get(request.path_params["locationId"])

        return models.JsonApiResponse(
            models.Body(
                data=resources.LocationResource.from_proto(location, request),
            ),
        )


class Locations(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: locations.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.find(limit=pagination.limit, cursor=pagination.cursor)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.LocationResource.from_proto(location, request)
                    for location in response.locations
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Locations"),
                    response.next_page_token,
                    pagination,
                ),
            ),
        )
