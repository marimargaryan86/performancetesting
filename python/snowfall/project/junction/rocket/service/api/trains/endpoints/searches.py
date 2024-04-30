import datetime
from collections.abc import Sequence

import grpc
import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.trains.endpoints import validation
from snowfall.project.junction.rocket.service.api.trains.models import (
    searches as search_models,
)
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2 as places_models_pb2,
)
from snowfall.project.junction.rocket.service.places.v1alpha import (
    places_pb2,
    places_pb2_grpc,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)

_IncludesType = search_models.ResultDetailResource | search_models.OfferResource


class TrainSearch(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def post(
        self,
        request: requests.Request,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        searches: grpc_pb2_grpc.SearchServiceStub = lagom.injectable,
        places: places_pb2_grpc.PlacesServiceStub = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        timeout = grpc_timeout.total_seconds()
        origin = await self._get_place(places, body["origin"], timeout)
        destination = await self._get_place(places, body["destination"], timeout)

        request_validator = validation.SearchRequestValidator(body, origin, destination)
        if request_validator.validation_errors:
            return request_validator.as_json_api_response()

        departure_before = body.get("departureBefore", None)
        if departure_before:
            departure_before = protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(departure_before),
            )

        return_date = body.get("returnAt", None)
        if return_date:
            return_date = protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(return_date),
            )

        response = await searches.EnqueueSearch(
            grpc_pb2.EnqueueSearchRequest(
                search=models_pb2.Search(
                    reseller_id=request.user.username,
                    rail=models_pb2.Rail(
                        origin=origin,
                        destination=destination,
                        departure_after=protobuf.datetime_to_protobuf(
                            datetime.datetime.fromisoformat(body["departureAfter"]),
                        ),
                        departure_before=departure_before,
                        return_date=return_date,
                        outbound_offer_id=body.get("selectedOutboundOffer", ""),
                        passengers=[
                            models_pb2.Passenger(
                                date_of_birth=protobuf.date_to_protobuf(
                                    datetime.date.fromisoformat(
                                        passenger["dateOfBirth"],
                                    ),
                                ),
                            )
                            for passenger in body["passengers"]
                        ],
                    ),
                ),
            ),
            timeout=grpc_timeout.total_seconds(),
        )

        return await messages.create_response(
            body=models.Body(
                data=search_models.TrainSearchResource.from_proto(
                    response.search,
                    request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    @errors.handle_grpc_errors
    async def get(
        self,
        request: requests.Request,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        searches: grpc_pb2_grpc.SearchServiceStub = lagom.injectable,
    ) -> responses.Response:
        search_id = request.path_params["searchId"]
        response = await searches.GetSearch(
            grpc_pb2.GetSearchRequest(id=search_id),
            timeout=grpc_timeout.total_seconds(),
        )

        return await messages.create_response(
            body=models.Body(
                data=search_models.TrainSearchResource.from_proto(
                    response.search,
                    request,
                ),
            ),
            request=request,
        )

    async def _get_place(
        self,
        places: places_pb2_grpc.PlacesServiceStub,
        place_id: str,
        timeout: float,
    ) -> places_models_pb2.Place | None:
        try:
            return (
                await places.GetPlace(
                    places_pb2.GetPlaceRequest(id=place_id),
                    timeout=timeout,
                )
            ).place
        except grpc.aio.AioRpcError as err:
            if err.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise


class TrainSearchResults(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def get(
        self,
        request: requests.Request,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        search_results: grpc_pb2_grpc.SearchResultServiceStub = lagom.injectable,
    ) -> responses.Response:
        search_id = request.path_params["searchId"]
        response = await search_results.ListSearchResults(
            grpc_pb2.ListSearchResultsRequest(search_id=search_id),
            timeout=grpc_timeout.total_seconds(),
        )

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=response.search_results,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    search_models.SearchResultResource.from_proto(
                        search_result,
                    )
                    for search_result in items_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListTrainsSearchResults",
                        searchId=search_id,
                    ),
                    items_page.cursor,
                    pagination,
                ),
                included=self._resolve_included(items_page.sequence, request),
            ),
            request=request,
        )

    def _resolve_included(
        self,
        search_results: Sequence[models_pb2.SearchResult],
        request: requests.Request,
    ) -> list[_IncludesType]:
        included: list[_IncludesType] = []
        requested_includes = request.scope["parsed_query_string"].get("include", [])
        if "offers" in requested_includes:
            included.extend([
                search_models.OfferResource.from_proto(offer)
                for search_result in search_results
                for offer in search_result.offers
            ])
        if "resultDetails" in requested_includes:
            included.extend([
                search_models.ResultDetailResource.from_proto(result_detail)
                for search_result in search_results
                for result_detail in search_result.result_details
            ])
        return included


class TrainOffers(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def get(
        self,
        request: requests.Request,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        offers: grpc_pb2_grpc.OfferServiceStub = lagom.injectable,
    ) -> responses.Response:
        offer_id = request.path_params["offerId"]
        response: grpc_pb2.GetOfferResponse = await offers.GetOffer(
            grpc_pb2.GetOfferRequest(id=offer_id),
            timeout=grpc_timeout.total_seconds(),
        )

        if not response.offer.HasField("rail"):
            return models.JsonApiResponse(
                models.Body(errors=[errors.generate_not_found_error("offerId")]),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return await messages.create_response(
            body=models.Body(
                data=search_models.OfferResource.from_proto(
                    response.offer,
                ),
            ),
            request=request,
        )
