import asyncio
import json

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.rocket.service.api.air.repositories import (
    AirSearchResultRepository,
)
from snowfall.project.junction.rocket.service.api.air.types import (
    AirSearchRequestTransformer,
    AirSearchResultTransformer,
)
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
)
from snowfall.vendor.junction_one.client import JunctionOneClient


class AirSearch(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_one_client: JunctionOneClient = lagom.injectable,
        air_search_request_transformer: AirSearchRequestTransformer = lagom.injectable,
        air_search_result_transformer: AirSearchResultTransformer = lagom.injectable,
        repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        query = air_search_request_transformer.transform(await request.json())
        response = await junction_one_client.search_flights(query)
        transformed = air_search_result_transformer.transform(response)
        await asyncio.gather(*(repo.insert(doc) for doc in transformed))

        response_model = {
            "id": transformed[0].search_id,
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
        repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        search_id: str = request.path_params["id"]

        search_status = "completed" if await repo.exists(search_id) else "processing"
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
        repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        result_set = await repo.find_by_search_id(request.path_params["id"])

        data = [
            models.Resource(
                id=result.id,
                type="search-result",
                relationships={
                    "offers": models.Relationship(
                        data=[
                            models.ResourceIdentifier(
                                id=offer.id,
                                type="offers",
                            )
                            for offer in result.offers
                        ],
                    ),
                    "resultDetails": models.Relationship(
                        data=[
                            models.ResourceIdentifier(
                                id=result_details.id,
                                type="result-details",
                            )
                            for result_details in result.result_details
                        ],
                    ),
                },
            )
            async for result in result_set
        ]

        return await messages.create_response(
            body=models.Body(data=data),
            request=request,
        )
