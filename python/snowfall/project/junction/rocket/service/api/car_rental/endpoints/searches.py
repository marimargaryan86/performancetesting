import datetime
from collections.abc import Sequence

import lagom
import timezonefinder
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.v1 import models_pb2 as legacy_go_pb2
from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.car_rental.endpoints import (
    searches_validation as validation,
)
from snowfall.project.junction.rocket.service.api.car_rental.models import (
    searches as search_models,
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
from snowfall.stdlib.v1 import latlng_pb2

_tz_finder = timezonefinder.TimezoneFinder()
_IncludesType = search_models.ResultDetailResource | search_models.OfferResource


class CarSearch(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def post(
        self,
        request: requests.Request,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        searches: grpc_pb2_grpc.SearchServiceStub = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        validation_errors = validation.validate_create_search_request(body)
        if validation_errors:
            return models.JsonApiResponse(
                models.Body(errors=validation_errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        origin_coords = latlng_pb2.LatLng(
            latitude=body["pickupLocation"]["latitude"],
            longitude=body["pickupLocation"]["longitude"],
        )

        origin_timezone = _tz_finder.timezone_at(
            lat=origin_coords.latitude,
            lng=origin_coords.longitude,
        )

        destination_coords = latlng_pb2.LatLng(
            latitude=body["returnLocation"]["latitude"],
            longitude=body["returnLocation"]["longitude"],
        )

        destination_timezone = _tz_finder.timezone_at(
            lat=destination_coords.latitude,
            lng=destination_coords.longitude,
        )

        response = await searches.EnqueueSearch(
            grpc_pb2.EnqueueSearchRequest(
                search=models_pb2.Search(
                    reseller_id=request.user.username,
                    car_rental=models_pb2.CarRental(
                        origin=legacy_go_pb2.Point(
                            coordinates=origin_coords,
                            time_zone=origin_timezone if origin_timezone else "",
                        ),
                        destination=legacy_go_pb2.Point(
                            coordinates=destination_coords,
                            time_zone=(
                                destination_timezone if destination_timezone else ""
                            ),
                        ),
                        pickup_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.fromisoformat(body["pickupAt"]),
                        ),
                        return_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.fromisoformat(body["returnAt"]),
                        ),
                        driver_age=body["driverAge"],
                    ),
                ),
            ),
            timeout=grpc_timeout.total_seconds(),
        )

        return await messages.create_response(
            body=models.Body(
                data=search_models.CarSearchResource.from_proto(
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
                data=search_models.CarSearchResource.from_proto(
                    response.search,
                    request,
                ),
            ),
            request=request,
        )


class CarSearchResults(endpoints.HTTPEndpoint):
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
                        "ListCarSearchResults",
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
