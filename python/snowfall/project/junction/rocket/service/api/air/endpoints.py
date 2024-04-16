import asyncio

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.rocket.service.api.air.models import (
    AirSearchRequestStorage,
    AirSearchResponseAttributes,
    StatusTypeEnum,
)
from snowfall.project.junction.rocket.service.api.air.repositories import (
    AirSearchRequestRepository,
    AirSearchResultRepository,
)
from snowfall.project.junction.rocket.service.api.air.types import (
    AirSearchRequestTransformer,
    AirSearchResultTransformer,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
)
from snowfall.vendor.junction_one.client import JunctionOneClient


class AirSearch(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_one_client: JunctionOneClient = lagom.injectable,
        air_search_request_transformer: AirSearchRequestTransformer = lagom.injectable,
        air_search_result_transformer: AirSearchResultTransformer = lagom.injectable,
        requests_repo: AirSearchRequestRepository = lagom.injectable,
        results_repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        reseller_id = request.user.username
        request_data = await request.json()

        query = air_search_request_transformer.transform(request_data)

        response = await junction_one_client.search_flights(query)
        transformed = air_search_result_transformer.transform(response)

        search_id = transformed[0].search_id
        insert_response = await requests_repo.insert(
            AirSearchRequestStorage(
                search_id=search_id,
                reseller_id=reseller_id,
                air=request_data["data"]["attributes"],
            ),
        )
        expires_at = insert_response.expires_at.isoformat()
        attributes_response = AirSearchResponseAttributes(
            **request_data["data"]["attributes"],
            status=StatusTypeEnum.pending,
            expires_at=expires_at,
        ).model_dump(by_alias=True, exclude_none=True)

        await asyncio.gather(*(results_repo.insert(doc) for doc in transformed))

        response_model = models.Resource(
            id=search_id,
            type="air-searches",
            attributes=attributes_response,
            links={
                "self": str(
                    request.url_for(
                        "AirSearch",
                    ),
                ),
            },
        )

        return await messages.create_response(
            body=models.Body(
                data=response_model,
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )


class AirSearchStatus(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        requests_repo: AirSearchRequestRepository = lagom.injectable,
        results_repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        search_id: str = request.path_params["searchId"]

        search_result_from_requests_repo = await requests_repo.find_by_search_id(
            search_id,
        )

        if not search_result_from_requests_repo:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        search_status = StatusTypeEnum.processing
        search_data = search_result_from_requests_repo.air.model_dump(by_alias=True)
        expires_at = search_result_from_requests_repo.expires_at.isoformat()

        search_result_from_results_repo = (
            await results_repo.find_any_result_by_search_id(search_id)
        )
        if search_result_from_results_repo:
            search_status = StatusTypeEnum.completed

        attributes_response = AirSearchResponseAttributes(
            **search_data,
            status=search_status,
            expires_at=expires_at,
        ).model_dump(by_alias=True, exclude_none=True)

        response_model = models.Resource(
            id=search_id,
            type="air-searches",
            attributes=attributes_response,
            links={
                "self": str(
                    request.url_for(
                        "AirSearchStatus",
                        searchId=request.path_params["searchId"],
                    ),
                ),
            },
        )

        return await messages.create_response(
            body=models.Body(
                data=response_model,
            ),
            request=request,
            status_code=status.HTTP_200_OK,
        )


class AirSearchRetrieval(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        requests_repo: AirSearchRequestRepository = lagom.injectable,
        results_repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        search_id = request.path_params["searchId"]

        search = await requests_repo.find_by_search_id(search_id)
        if not search:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        expires_at = search.expires_at.isoformat()
        search_data = search.air.model_dump(by_alias=True)

        result_set = await results_repo.find_results_by_search_id(search_id)

        # TODO(jeremy): fix includes resource
        data = [
            models.Resource(
                id=result.id,
                type="search-results",
                attributes=AirSearchResponseAttributes(
                    **search_data,
                    status=StatusTypeEnum.completed,
                    expires_at=expires_at,
                ).model_dump(by_alias=True, exclude_none=True),
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
                    "search": models.Relationship(
                        data=models.ResourceIdentifier(
                            id=request.path_params["searchId"],
                            type="air-searches",
                        ),
                    ),
                },
            )
            async for result in result_set
        ]

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=data,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=data,
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "AirSearchRetrieval",
                        searchId=request.path_params["searchId"],
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
            request=request,
        )
