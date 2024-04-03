import json

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.rocket.service.api.air.types import (
    AbstractAirSearchRepo,
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

        await repo.insert(transformed)

        response_model = {
            "id": transformed.id,
            "attributes": {
                "status": "pending",
            },
        }

        json_model = json.dumps(response_model)
        return responses.Response(status_code=status.HTTP_200_OK, content=json_model)


class AirSearchStatus(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repo: AbstractAirSearchRepo = lagom.injectable,
    ) -> responses.Response:
        search_id: str = request.path_params["id"]

        search_status = (
            "completed" if await repo.exists_id(search_id=search_id) else "processing"
        )
        response_model = {
            "id": search_id,
            "attributes": {
                "status": search_status,
            },
        }

        json_model = json.dumps(response_model)
        return responses.Response(status_code=status.HTTP_200_OK, content=json_model)


class AirSearchRetrieval(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repo: AbstractAirSearchRepo = lagom.injectable,
    ) -> responses.Response:
        model = await repo.find_by_id(request.path_params["id"])
        return responses.Response(
            status_code=status.HTTP_200_OK,
            content=model.model_dump_json(exclude_none=True),
        )
