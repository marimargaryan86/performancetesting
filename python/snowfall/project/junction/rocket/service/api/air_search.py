import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.rocket.service.api.repositories import (
    AbstractAirSearchRepo,
)
from snowfall.project.junction.rocket.service.api.types import (
    AirSearchRequestTransformer,
    AirSearchResultTransformer,
)
from snowfall.vendor.junction_one.client import JunctionOneClient


class AirSearch(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_one_client: JunctionOneClient = lagom.injectable,
        air_search_request_transformer: AirSearchRequestTransformer = lagom.injectable,
        air_search_result_transformer: AirSearchResultTransformer = lagom.injectable,
        repo: AbstractAirSearchRepo = lagom.injectable,
    ) -> responses.Response:
        query = air_search_request_transformer.transform(await request.json())
        response = await junction_one_client.search_flights(query)
        transformed = air_search_result_transformer.transform(response)

        repo.insert(transformed)

        json_model = transformed.model_dump_json(exclude_none=True)
        return responses.Response(status_code=status.HTTP_200_OK, content=json_model)
