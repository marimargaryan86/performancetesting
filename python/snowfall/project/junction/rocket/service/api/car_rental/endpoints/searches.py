import datetime
from collections.abc import Sequence

import grpc
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
        places: places_pb2_grpc.PlacesServiceStub = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        timeout = grpc_timeout.total_seconds()

        origin_place = await self._get_place(places, body["origin"], timeout)
        destination_place = await self._get_place(places, body["destination"], timeout)

        request_validator = validation.SearchRequestValidator(
            body,
            origin_place,
            destination_place,
        )

        if request_validator.validation_errors:
            return request_validator.as_json_api_response()

        response = await searches.EnqueueSearch(
            grpc_pb2.EnqueueSearchRequest(
                search=models_pb2.Search(
                    reseller_id=request.user.username,
                    car_rental=models_pb2.CarRental(
                        origin_id=body["origin"],
                        destination_id=body["destination"],
                        origin=legacy_go_pb2.Point(
                            coordinates=origin_place.coordinates,  # type: ignore[union-attr]
                            time_zone=origin_place.time_zone,  # type: ignore[union-attr]
                        ),
                        destination=legacy_go_pb2.Point(
                            coordinates=destination_place.coordinates,  # type: ignore[union-attr]
                            time_zone=destination_place.time_zone,  # type: ignore[union-attr]
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

    async def _get_place_coordinates(
        self,
        places: places_pb2_grpc.PlacesServiceStub,
        place_id: str,
        timeout: float,
    ) -> latlng_pb2.LatLng | None:
        try:
            place_response: places_pb2.GetPlaceResponse = await places.GetPlace(
                places_pb2.GetPlaceRequest(
                    id=place_id,
                ),
                timeout=timeout,
            )
        except grpc.aio.AioRpcError as err:
            if err.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise
        else:
            return latlng_pb2.LatLng(
                latitude=place_response.place.coordinates.latitude,
                longitude=place_response.place.coordinates.longitude,
            )

    def _get_timezone(self, coordinates: latlng_pb2.LatLng | None) -> str:
        if coordinates:
            return (
                _tz_finder.timezone_at(
                    lat=coordinates.latitude,
                    lng=coordinates.longitude,
                )
                or ""
            )

        return ""


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
