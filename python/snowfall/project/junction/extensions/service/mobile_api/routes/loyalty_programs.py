import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.extensions.service.mobile_api import (
    repository,
    resources,
)
from snowfall.stdlib.integration.starlette import models, pagination_helpers

_SEARCH_KEY = "query[name]"


class Programs(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        loyalty_programs_repository: repository.LoyaltyProgramsRepository = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)

        search_key = request.query_params.get(_SEARCH_KEY)
        programs = await loyalty_programs_repository.find(
            cursor=pagination.cursor,
            limit=pagination.limit,
            search_key=search_key,
        )
        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.LoyaltyProgram.from_proto(program=program)
                    async for program in programs
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListLoyaltyPrograms"),
                    await programs.cursor(),
                    pagination,
                ),
            ),
        )
