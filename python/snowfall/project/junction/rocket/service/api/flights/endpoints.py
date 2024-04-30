import json

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.flights import amqp
from snowfall.project.junction.rocket.service.api.flights.models import (
    FlightSearchRequest,
    FlightSearchRequestStorage,
    FlightSearchResponseAttributes,
    FlightSearchResultResource,
    StatusTypeEnum,
)
from snowfall.project.junction.rocket.service.api.flights.repositories import (
    FlightSearchRequestRepository,
    FlightSearchResultRepository,
)
from snowfall.project.junction.rocket.service.api.flights.validation import (
    SearchRequestValidator,
)
from snowfall.stdlib import sequence, string
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
)


def _is_inbound(
    flight_search_request: FlightSearchRequest,
) -> bool:
    return flight_search_request.data.relationships.selected_outbound_offer is not None


async def get_selected_outbound_offer_ref_ids(
    outbound_offer_id: str,
    results_repo: FlightSearchResultRepository,
) -> str:
    search_result = await results_repo.find_result_by_offer_id(
        outbound_offer_id,
    )
    selected_offer = next(
        offer for offer in search_result.offers if offer.id == outbound_offer_id
    )
    return selected_offer.ref_ids[0]


def _validate_request(search_request: FlightSearchRequest) -> None:
    if _is_inbound(search_request):
        relationships = search_request.data.relationships
        if relationships.selected_outbound_offer is None:
            raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST)


class FlightSearch(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def post(  # noqa: WPS217
        self,
        request: requests.Request,
        requests_repo: FlightSearchRequestRepository = lagom.injectable,
        search_task_producer: amqp.SearchTaskProducer = lagom.injectable,
    ) -> responses.Response:
        reseller_id = request.user.username
        request_data = await request.json()
        search_id = string.uuid()

        request_validator = SearchRequestValidator(request_data)
        if request_validator.validation_errors:
            return request_validator.as_json_api_response()

        search_request = FlightSearchRequest(**request_data)

        _validate_request(search_request)

        insert_response = await requests_repo.insert(
            FlightSearchRequestStorage(
                id=search_id,
                reseller_id=reseller_id,
                flight=request_data["data"]["attributes"],
            ),
        )

        await search_task_producer.publish(
            search_id=search_id,
            search_request_json=json.dumps(request_data),
            reseller_id=reseller_id,
            expires_at=insert_response.expires_at,
        )

        expires_at = insert_response.expires_at.isoformat()
        attributes_response = FlightSearchResponseAttributes(
            **request_data["data"]["attributes"],
            status=StatusTypeEnum.pending,
            expires_at=expires_at,
        ).model_dump(by_alias=True, exclude_none=True)

        response_model = models.Resource(
            id=search_id,
            type="flight-searches",
            attributes=attributes_response,
            links={
                "self": str(
                    request.url_for(
                        "FlightsSearch",
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


class FlightSearchStatus(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        requests_repo: FlightSearchRequestRepository = lagom.injectable,
        results_repo: FlightSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        search_id: str = request.path_params["searchId"]

        search_result_from_requests_repo = await requests_repo.find_by_search_id(
            search_id,
        )

        if not search_result_from_requests_repo:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        search_status = StatusTypeEnum.processing
        search_data = search_result_from_requests_repo.flight.model_dump(by_alias=True)
        expires_at = search_result_from_requests_repo.expires_at.isoformat()

        search_result_from_results_repo = (
            await results_repo.find_any_result_by_search_id(search_id)
        )
        if search_result_from_results_repo:
            search_status = StatusTypeEnum.completed

        attributes_response = FlightSearchResponseAttributes(
            **search_data,
            status=search_status,
            expires_at=expires_at,
        ).model_dump(by_alias=True, exclude_none=True)

        response_model = models.Resource(
            id=search_id,
            type="flight-searches",
            attributes=attributes_response,
            links={
                "self": str(
                    request.url_for(
                        "FlightsSearchStatus",
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


class FlightSearchRetrieval(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        requests_repo: FlightSearchRequestRepository = lagom.injectable,
        results_repo: FlightSearchResultRepository = lagom.injectable,
    ) -> responses.Response:
        search_id = request.path_params["searchId"]
        search = await requests_repo.find_by_search_id(search_id)
        if not search:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        result_set = await results_repo.find_results_by_search_id(search_id)

        response_data = [
            FlightSearchResultResource.from_model(
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
                        "FlightsSearchRetrieval",
                        searchId=request.path_params["searchId"],
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
            request=request,
        )
