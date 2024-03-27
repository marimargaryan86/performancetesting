import datetime

import lagom
import timezonefinder
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.v1 import models_pb2 as legacy_go_pb2
from snowfall.project.junction.rocket.adapter import search_results, searches
from snowfall.project.junction.rocket.service.api.car_rental.models import (
    searches as search_models,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
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


class CarSearch(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        client: searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

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

        search = await client.create(
            models_pb2.Search(
                reseller_id=request.user.username,
                car_rental=models_pb2.CarRental(
                    origin=legacy_go_pb2.Point(
                        coordinates=origin_coords,
                        time_zone=origin_timezone if origin_timezone else "",
                    ),
                    destination=legacy_go_pb2.Point(
                        coordinates=destination_coords,
                        time_zone=destination_timezone if destination_timezone else "",
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
        )

        return await messages.create_response(
            body=models.Body(
                data=search_models.CarSearchResource.from_proto(search, request),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        client: searches.Client = lagom.injectable,
    ) -> responses.Response:
        search_id = request.path_params["searchId"]
        search = await client.get(search_id)

        return await messages.create_response(
            body=models.Body(
                data=search_models.CarSearchResource.from_proto(search, request),
            ),
            request=request,
        )


class CarSearchResults(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: search_results.Client = lagom.injectable,
    ) -> responses.Response:
        search_id = request.path_params["searchId"]
        results = await client.get_search_results_by_search_id(search_id)

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=results,
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
            ),
            request=request,
        )
