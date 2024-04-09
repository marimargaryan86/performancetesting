import datetime

import lagom
import timezonefinder
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.v1 import models_pb2 as legacy_go_pb2
from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.rail.models import (
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


class RailSearch(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def post(
        self,
        request: requests.Request,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        searches: grpc_pb2_grpc.SearchServiceStub = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        origin_coords = latlng_pb2.LatLng(
            latitude=body["origin"]["latitude"],
            longitude=body["origin"]["longitude"],
        )

        origin_timezone = _tz_finder.timezone_at(
            lat=origin_coords.latitude,
            lng=origin_coords.longitude,
        )

        destination_coords = latlng_pb2.LatLng(
            latitude=body["destination"]["latitude"],
            longitude=body["destination"]["longitude"],
        )

        destination_timezone = _tz_finder.timezone_at(
            lat=destination_coords.latitude,
            lng=destination_coords.longitude,
        )

        departure_before = body.get("departureBefore", None)
        if departure_before:
            departure_before = protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(departure_before),
            )

        response = await searches.EnqueueSearch(
            grpc_pb2.EnqueueSearchRequest(
                search=models_pb2.Search(
                    reseller_id=request.user.username,
                    rail=models_pb2.Rail(
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
                        departure_after=protobuf.datetime_to_protobuf(
                            datetime.datetime.fromisoformat(body["departureAfter"]),
                        ),
                        departure_before=departure_before,
                        return_date=protobuf.datetime_to_protobuf(
                            datetime.datetime.fromisoformat(body["returnAt"]),
                        ),
                        outbound_search_result_id=body.get("selectedOutboundOffer", ""),
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
                data=search_models.RailSearchResource.from_proto(
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
                data=search_models.RailSearchResource.from_proto(
                    response.search,
                    request,
                ),
            ),
            request=request,
        )


class RailSearchResults(endpoints.HTTPEndpoint):
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
                        "ListRailSearchResults",
                        searchId=search_id,
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
            request=request,
        )
