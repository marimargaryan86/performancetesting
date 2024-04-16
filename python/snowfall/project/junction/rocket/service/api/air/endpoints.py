import asyncio
from datetime import UTC, date, datetime

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.rocket.service.api.air.models import (
    AirSearchRequestStorage,
    AirSearchResponseAttributes,
    Passenger,
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
        request_repo: AirSearchRequestRepository = lagom.injectable,
        result_repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        request_data = await request.json()

        query = air_search_request_transformer.transform(request_data)

        response = await junction_one_client.search_flights(query)
        transformed = air_search_result_transformer.transform(response)

        search_id = transformed[0].search_id
        await request_repo.insert(
            AirSearchRequestStorage(
                search_id=search_id,
                reseller_id="air",
                air=request_data["data"]["attributes"],
            ),
        )
        # TODO(jeremy): fix response model here for unit tests
        attributes_response = AirSearchResponseAttributes(
            **request_data["data"]["attributes"],
            status=StatusTypeEnum.pending,
            expires_at="2024-04-11T12:30:45Z",  # TODO(jeremy): fix hc expiry time
        ).model_dump(by_alias=True, exclude_none=True)

        await asyncio.gather(*(result_repo.insert(doc) for doc in transformed))

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
        repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        search_id: str = request.path_params["searchId"]

        search_status = (
            StatusTypeEnum.completed
            if await repo.find_any_result_by_search_id(search_id)
            else StatusTypeEnum.processing
        )

        # TODO(jeremy): fix hardcoded data of response attributes
        # TODO(jeremy): blocked by MR(https://git.snowfall.se/junction/junction/-/merge_requests/5083) to get mongo search object
        attributes_response = AirSearchResponseAttributes(
            departure_at=datetime.now(tz=UTC),
            origin="LON",
            destination="PAR",
            passengers=[Passenger(date_of_birth=date.fromisoformat("1980-01-01"))],
            status=StatusTypeEnum(search_status),
            expires_at="2024-04-11T12:30:45Z",
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
        repo: AirSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        result_set = await repo.find_results_by_search_id(
            request.path_params["searchId"],
        )

        # TODO(jeremy): fix includes resource
        data = [
            models.Resource(
                id=result.id,
                type="search-results",
                attributes={
                    "expiresAt": "2024-04-11T12:30:45Z",  # TODO(jeremy): fix hc expiry time
                },
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
