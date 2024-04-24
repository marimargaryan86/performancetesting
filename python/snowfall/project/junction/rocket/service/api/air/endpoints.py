import asyncio

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.air.models import (
    AirSearchRequest,
    AirSearchRequestStorage,
    AirSearchResponseAttributes,
    AirSearchResultResource,
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
from snowfall.project.junction.rocket.service.places.v1alpha import (
    places_pb2_grpc,
)
from snowfall.stdlib import sequence, string
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
)
from snowfall.vendor.junction_one.client import JunctionOneClient


def is_inbound(
    air_search_request: AirSearchRequest,
) -> bool:
    return air_search_request.data.relationships.selected_outbound_offer is not None


async def get_selected_outbound_offer_ref_ids(
    outbound_offer_id: str,
    results_repo: AirSearchResultRepository,
) -> str:
    search_result = await results_repo.find_result_by_offer_id(
        outbound_offer_id,
    )
    selected_offer = next(
        offer for offer in search_result.offers if offer.id == outbound_offer_id
    )
    return selected_offer.ref_ids[0]


class AirSearch(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def post(  # noqa: WPS217
        self,
        request: requests.Request,
        junction_one_client: JunctionOneClient = lagom.injectable,
        air_search_request_transformer: AirSearchRequestTransformer = lagom.injectable,
        air_search_result_transformer: AirSearchResultTransformer = lagom.injectable,
        requests_repo: AirSearchRequestRepository = lagom.injectable,
        results_repo: AirSearchResultRepository = lagom.injectable,
        places: places_pb2_grpc.PlacesServiceStub = lagom.injectable,
    ) -> responses.Response:
        reseller_id = request.user.username
        request_data = await request.json()
        search_id = string.uuid()

        search_request = AirSearchRequest(**request_data)
        if is_inbound(search_request):
            relationships = search_request.data.relationships
            if relationships is None:
                raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST)
            if relationships.selected_outbound_offer is None:
                raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST)

            outbound_flight_ref_id = await get_selected_outbound_offer_ref_ids(
                outbound_offer_id=relationships.selected_outbound_offer.data.id,
                results_repo=results_repo,
            )

            query = await air_search_request_transformer.transform_inbound_query(
                search_request,
                outbound_flight_ref_id,
                places,
            )
        else:
            query = await air_search_request_transformer.transform_outbound_query(
                search_request,
                places,
            )
        j1_search_response = await junction_one_client.search_flights(query)
        transformed = air_search_result_transformer.transform(
            j1_search_response,
            search_id,
        )

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

        result_set = await results_repo.find_results_by_search_id(search_id)

        response_data = [
            AirSearchResultResource.from_model(
                search_result=search_result,
                search=search,
            )
            async for search_result in result_set
        ]

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=response_data,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=response_data,
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
