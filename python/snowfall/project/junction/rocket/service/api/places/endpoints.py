import datetime

import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.places.models import (
    places as place_models,
)
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.format.protobuf import slug_to_enum_value
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
)
from snowfall.stdlib.v1 import latlng_pb2

DEFAULT_RADIUS = 1000
DEFAULT_PAGE_LIMIT = 20


class GetPlace(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def get(
        self,
        request: requests.Request,
        places: places_pb2_grpc.PlacesServiceStub = lagom.injectable,
        grpc_timeout: datetime.timedelta = lagom.injectable,
    ) -> responses.Response:
        path_params = request.path_params
        place_id = path_params["placeId"]

        response = await places.GetPlace(
            places_pb2.GetPlaceRequest(id=place_id),
            timeout=grpc_timeout.total_seconds(),
        )

        return await messages.create_response(
            body=models.Body(
                data=place_models.PlacesResource.from_proto(
                    response.place,
                    request,
                ),
            ),
            request=request,
        )


class GetPlaces(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def get(
        self,
        request: requests.Request,
        places: places_pb2_grpc.PlacesServiceStub = lagom.injectable,
        grpc_timeout: datetime.timedelta = lagom.injectable,
    ) -> responses.Response:
        filter_iata = request.scope["parsed_query_string"].get("filter[iata][eq]")
        if filter_iata:
            filter_iata = filter_iata[0]
            return await self._get_place_by_iata(
                request,
                places,
                grpc_timeout,
                filter_iata,
            )
        return await self._list_places(request, places, grpc_timeout)

    async def _list_places(
        self,
        request: requests.Request,
        places: places_pb2_grpc.PlacesServiceStub,
        grpc_timeout: datetime.timedelta,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        filters_kwargs = {}
        filter_name = request.scope["parsed_query_string"].get("filter[name][like]")
        if filter_name:
            filters_kwargs["name"] = filter_name
        filter_types = request.scope["parsed_query_string"].get("filter[type][eq]")
        if filter_types:
            enum_types = [
                slug_to_enum_value(models_pb2.Type, type_) for type_ in filter_types
            ]
            filters_kwargs["types"] = enum_types
        query_coordinates = request.scope["parsed_query_string"].get(
            "query[coordinates]",
        )
        if query_coordinates:
            filters_kwargs["coordinates_and_radius"] = models_pb2.CoordinatesAndRadius(
                coordinates=latlng_pb2.LatLng(
                    latitude=float(query_coordinates[1]),
                    longitude=float(query_coordinates[0]),
                ),
                radius=int(query_coordinates[2])
                if len(query_coordinates) == 3
                else DEFAULT_RADIUS,
            )
        place_to_search_within = request.scope["parsed_query_string"].get(
            "query[placeToSearchWithin]",
        )
        if place_to_search_within:
            filters_kwargs["place_to_search_within_id"] = str(place_to_search_within)
        response = await places.ListPlaces(
            places_pb2.ListPlacesRequest(
                page_size=DEFAULT_PAGE_LIMIT
                if pagination.limit is None
                else pagination.limit,
                page_token="" if pagination.cursor is None else pagination.cursor,
                filters=places_pb2.Filters(**filters_kwargs),
            ),
            timeout=grpc_timeout.total_seconds(),
        )
        query_params = dict(request.query_params)
        query_params.pop("page[cursor]", None)
        query_params.pop("page[limit]", None)
        return await messages.create_response(
            body=models.Body(
                data=[
                    place_models.PlacesResource.from_proto(place, request)
                    for place in response.places
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("GetPlaces").include_query_params(**query_params),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )

    async def _get_place_by_iata(
        self,
        request: requests.Request,
        places: places_pb2_grpc.PlacesServiceStub,
        grpc_timeout: datetime.timedelta,
        iata: str,
    ) -> responses.Response:
        response = await places.GetPlaceByIata(
            places_pb2.GetPlaceByIataRequest(iata=iata),
            timeout=grpc_timeout.total_seconds(),
        )
        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=[response.place],
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    place_models.PlacesResource.from_proto(place, request)
                    for place in items_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("GetPlaces").include_query_params(
                        **request.query_params,
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
            request=request,
        )
