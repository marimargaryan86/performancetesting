import json

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.rocket.service.api.hotel import types
from snowfall.vendor.junction_one.client import JunctionOneClient


class HotelSearch(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_one_client: JunctionOneClient = lagom.injectable,
        hotel_search_request_transformer: types.HotelSearchRequestTransformer = lagom.injectable,
        hotel_search_result_transformer: types.HotelSearchResultTransformer = lagom.injectable,
        repo: types.AbstractHotelSearchRepo = lagom.injectable,
    ) -> responses.Response:
        query = hotel_search_request_transformer.transform(await request.json())
        response = await junction_one_client.search_hotels(query)
        transformed = hotel_search_result_transformer.transform(response)

        await repo.insert(transformed)

        response_model = {
            "id": transformed.id,
            "attributes": {
                "status": "pending",
            },
        }

        json_model = json.dumps(response_model)
        return responses.Response(status_code=status.HTTP_200_OK, content=json_model)


class HotelSearchStatus(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repo: types.AbstractHotelSearchRepo = lagom.injectable,
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


class HotelSearchRetrieval(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repo: types.AbstractHotelSearchRepo = lagom.injectable,
    ) -> responses.Response:
        model = await repo.find_by_id(request.path_params["id"])
        return responses.Response(
            status_code=status.HTTP_200_OK,
            content=model.model_dump_json(exclude_none=True),
        )
