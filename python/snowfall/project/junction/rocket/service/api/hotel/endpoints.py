import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.rocket.service.api.hotel import types
from snowfall.project.junction.rocket.service.api.hotel.models import (
    HotelRoomsSearchResult,
    RoomsResult,
)
from snowfall.project.junction.rocket.service.api.hotel.repositories import (
    HotelRoomsSearchRepository,
    HotelSearchRepository,
)
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
)
from snowfall.vendor.junction_one.client import JunctionOneClient
from snowfall.vendor.junction_one.models.base import HotelDetailsRequest


class HotelSearch(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_one_client: JunctionOneClient = lagom.injectable,
        hotel_search_request_transformer: types.HotelSearchRequestTransformer = lagom.injectable,
        hotel_search_result_transformer: types.HotelSearchResultTransformer = lagom.injectable,
        repo: HotelSearchRepository = lagom.injectable,
    ) -> responses.Response:
        query = hotel_search_request_transformer.transform(await request.json())
        response = await junction_one_client.search_hotels(query)
        transformed = hotel_search_result_transformer.transform(response)

        await repo.insert(transformed)

        return await messages.create_response(
            body=models.Body(
                data=models.Resource(
                    id=transformed.id,
                    type="hotel-search",
                    attributes={"status": "pending"},
                ),
            ),
            request=request,
        )


class HotelSearchStatus(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repo: HotelSearchRepository = lagom.injectable,
    ) -> responses.Response:
        search_id: str = request.path_params["id"]

        search_status = "completed" if await repo.exists(search_id) else "processing"
        return await messages.create_response(
            body=models.Body(
                data=models.Resource(
                    id=search_id,
                    type="hotel-search",
                    attributes={"status": search_status},
                ),
            ),
            request=request,
        )


class HotelSearchRetrieval(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repo: HotelSearchRepository = lagom.injectable,
    ) -> responses.Response:
        model = await repo.find_by_id(request.path_params["id"])
        if not model:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return await messages.create_response(
            body=models.Body(
                data=models.Resource(
                    id=model.id,
                    type="hotel-search",
                    attributes=model.model_dump(exclude_none=True),
                ),
            ),
            request=request,
        )


class HotelRoomsSearch(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_one_client: JunctionOneClient = lagom.injectable,
        repo: HotelRoomsSearchRepository = lagom.injectable,
    ) -> responses.Response:
        attributes = (await request.json())["data"]["attributes"]
        response = await junction_one_client.get_hotel_details(
            HotelDetailsRequest(refs=[attributes["ref"]]),
        )

        transformed = HotelRoomsSearchResult(
            id=string.uuid(),
            data=[RoomsResult(**room.model_dump()) for room in response.rooms or []],
        )

        await repo.insert(transformed)

        return await messages.create_response(
            body=models.Body(
                data=models.Resource(
                    id=transformed.id,
                    type="hotel-rooms-search",
                    attributes={"status": "pending"},
                ),
            ),
            request=request,
        )


class HotelRoomsSearchStatus(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repo: HotelRoomsSearchRepository = lagom.injectable,
    ) -> responses.Response:
        search_id: str = request.path_params["id"]
        search_status = "completed" if await repo.exists(search_id) else "processing"
        return await messages.create_response(
            body=models.Body(
                data=models.Resource(
                    id=search_id,
                    type="hotel-rooms-search",
                    attributes={"status": search_status},
                ),
            ),
            request=request,
        )


class HotelRoomsSearchRetrieval(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repo: HotelRoomsSearchRepository = lagom.injectable,
    ) -> responses.Response:
        model = await repo.find_by_id(request.path_params["id"])
        if not model:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return await messages.create_response(
            body=models.Body(
                data=models.Resource(
                    id=model.id,
                    type="hotel-rooms-search",
                    attributes=model.model_dump(exclude_none=True),
                ),
            ),
            request=request,
        )
