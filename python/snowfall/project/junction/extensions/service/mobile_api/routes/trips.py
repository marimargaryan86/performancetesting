import re

import lagom
from dateutil import parser
from starlette import endpoints, requests, responses, status

from snowfall.stdlib.integration.starlette import (
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.vendor.junction.go import client


class TripSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        junction_trip_search = await junction_client.trips().create_trip_search(
            origin_id=body["origin"],
            destination_id=body["destination"],
            departure_after=parser.parse(body["departureAfter"]),
            allowed_segment_types=[
                client.LegType(leg_type)
                for leg_type in body.get("allowedSegmentTypes", [])
            ],
        )

        return models.JsonApiResponse(
            models.Body(
                data=junction_trip_search["data"],
            ),
            status.HTTP_201_CREATED,
        )


class TripSearchesTrips(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        trip_search = await junction_client.trips().get_trips_by_trip_search_id(
            trips_search_id=request.path_params["tripSearchId"],
            include=request.scope["parsed_query_string"].get(
                "include",
                [],
            ),
            cursor=pagination.cursor,
            limit=pagination.limit,
        )
        response_body = models.Body(
            data=trip_search["data"],
            links={
                # TODO: make a function inside pagination_helpers for that
                "next": re.sub(
                    r"^.+\?",
                    str(
                        request.url_for(
                            "TripSearchesTrips",
                            tripSearchId=request.path_params["tripSearchId"],
                        ),
                    )
                    + str("?"),
                    trip_search["links"]["next"],
                ),
            },
        )
        if trip_search.get("included"):
            response_body.included = trip_search.get("included")
        return models.JsonApiResponse(response_body)
