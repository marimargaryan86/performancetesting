import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.go.service.data_api import resources
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1alpha import latlng_pb2

_DEFAULT_LIMIT = 50


class Locations(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        geocoder: geocoding_pb2_grpc.GeocodingServiceStub = lagom.injectable,
    ) -> responses.Response:
        bias_position = None
        query_string = request.scope["parsed_query_string"]
        if query_string.get("query[biasPosition]"):
            bias_long, bias_lat = query_string.get(
                "query[biasPosition]",
            ).split(
                ",",
            )
            bias_position = latlng_pb2.LatLng(
                latitude=float(bias_lat),
                longitude=float(bias_long),
            )
        locations_response = await geocoder.LocationLookup(
            geocoding_pb2.LocationLookupRequest(
                language=query_string.get(
                    "query[language]",
                    "en",
                ),
                limit=int(
                    query_string.get(
                        "page[limit]",
                        _DEFAULT_LIMIT,
                    ),
                ),
                text=query_string["query[text]"],
                countries=query_string.get("query[countries]"),
                bias_position=bias_position,
            ),
        )
        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.LocationResource.from_proto(location)
                    for location in locations_response.locations
                ],
            ),
        )
