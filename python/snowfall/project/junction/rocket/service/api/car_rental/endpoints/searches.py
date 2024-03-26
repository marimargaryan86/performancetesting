import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.rocket.adapter import search_results
from snowfall.project.junction.rocket.service.api.car_rental.models import (
    searches as search_models,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
)


class CarSearchResults(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: search_results.Client = lagom.injectable,
    ) -> responses.Response:
        search_id = request.path_params["searchId"]
        results = await client.get_search_results_by_search_id(search_id)

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=results,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    search_models.SearchResultResource.from_proto(
                        search_result,
                        request,
                    )
                    for search_result in items_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListCarSearchResults",
                        searchId=search_id,
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
            request=request,
        )
