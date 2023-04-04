import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.service.data_api import resources
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1alpha import latlng_pb2

_DEFAULT_LIMIT = 50


class Coordinates(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        geocoder: geocoding_pb2_grpc.GeocodingServiceStub = lagom.injectable,
    ) -> responses.Response:
        bias_position = None
        bias_position_str = request.query_params.get("query[biasPosition]")
        if bias_position_str:
            bias_long, bias_lat = bias_position_str.split(
                ",",
            )
            bias_position = latlng_pb2.LatLng(
                latitude=float(bias_lat),
                longitude=float(bias_long),
            )
        coordinates_response = await geocoder.LocationLookup(
            geocoding_pb2.LocationLookupRequest(
                language=request.query_params.get("query[language]", "en"),
                limit=int(
                    request.query_params.get("page[limit]", _DEFAULT_LIMIT),
                ),
                text=request.query_params["query[text]"],
                countries=request.query_params.get("query[countries]"),
                bias_position=bias_position,
            ),
        )
        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.CoordinateResource.from_proto(coordinates)
                    for coordinates in coordinates_response.coordinates
                ],
            ),
        )
