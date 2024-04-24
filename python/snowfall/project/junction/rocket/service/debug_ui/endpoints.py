from collections.abc import Mapping
from typing import cast

from google.protobuf import json_format
from starlette import responses, templating

from snowfall.project.junction.go.service.places.v1 import places_pb2, places_pb2_grpc
from snowfall.project.junction.go.service.planner.v1 import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.stdlib.integration.starlette import messages


class Locations:
    def __init__(
        self,
        locations: places_pb2_grpc.LocationsServiceStub,
    ):
        self._locations = locations

    async def post(
        self,
        request: messages.Request,
    ) -> responses.Response:
        response = cast(
            places_pb2.ListLocationsResponse,
            await self._locations.ListLocations(
                request=json_format.ParseDict(
                    js_dict=request.body,
                    message=places_pb2.ListLocationsRequest(),
                ),
            ),
        )

        return responses.JSONResponse(
            content=json_format.MessageToDict(
                response,
                including_default_value_fields=True,
            ),
        )

    async def post_near(
        self,
        request: messages.Request,
    ) -> responses.Response:
        response = cast(
            places_pb2.ListNearbyLocationsResponse,
            await self._locations.ListNearbyLocations(
                request=json_format.ParseDict(
                    js_dict=request.body,
                    message=places_pb2.ListNearbyLocationsRequest(),
                ),
            ),
        )

        return responses.JSONResponse(
            content=json_format.MessageToDict(
                response,
                including_default_value_fields=True,
            ),
        )


class Places:
    def __init__(
        self,
        places: places_pb2_grpc.PlacesServiceStub,
    ):
        self._places = places

    async def post(
        self,
        request: messages.Request,
    ) -> responses.Response:
        response = cast(
            places_pb2.ListPlacesResponse,
            await self._places.ListPlaces(
                request=json_format.ParseDict(
                    js_dict=request.body,
                    message=places_pb2.ListPlacesRequest(),
                ),
            ),
        )

        return responses.JSONResponse(
            content=json_format.MessageToDict(
                response,
                including_default_value_fields=True,
            ),
        )


class Routes:
    def __init__(
        self,
        planner: planner_pb2_grpc.PlannerServiceStub,
    ):
        self._planner = planner

    async def post(
        self,
        request: messages.Request,
    ) -> responses.Response:
        response = cast(
            planner_pb2.FindRoutesResponse,
            await self._planner.FindRoutes(
                request=json_format.ParseDict(
                    js_dict=request.body,
                    message=planner_pb2.FindRoutesRequest(),
                ),
            ),
        )

        return responses.JSONResponse(
            content=json_format.MessageToDict(
                response,
                including_default_value_fields=True,
            ),
        )


class UI:
    def __init__(
        self,
        templates: templating.Jinja2Templates,
        static_resources: Mapping[str, str],
    ):
        self._static_resources = static_resources
        self._templates = templates

    async def get(
        self,
        request: messages.Request,
    ) -> responses.Response:
        return self._templates.TemplateResponse(
            "layout.html",
            {
                "hashes": self._static_resources,
                "request": request.starlette_request,
            },
        )
