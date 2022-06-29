import asyncio

import lagom
from dateutil import parser
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.junction.mobile_api import repository, resources
from snowfall.junction.mobile_api.tasks import trips
from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.vendor.junction import client


class TripSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        trip_searches_repository: repository.TripSearchesRepository = lagom.injectable,
        trips_repository: repository.TripsRepository = lagom.injectable,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        junction_trip_search = await junction_client.create_trip_search(
            origin_id=body["origin"],
            destination_id=body["destination"],
            departure_after=parser.parse(body["departureAfter"]),
            leg_types=[client.LegType(leg_type) for leg_type in body["legTypes"]],
        )
        trip_search = await trip_searches_repository.create_trip_search(
            junction_trip_search,
            await request.json(),
        )

        asyncio.create_task(
            trips.poll_trips(
                junction_trip_search["data"]["id"],
                trip_searches_repository,
                trips_repository,
                junction_client,
            ),
        )

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripSearchResource.from_mongo(trip_search),
            ),
            status.HTTP_201_CREATED,
        )


class TripSearchesTrips(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        trip_searches_repository: repository.TripSearchesRepository = lagom.injectable,
    ) -> responses.Response:
        trip_search_trips = await trip_searches_repository.get_trips(
            request.path_params["tripSearchId"],
        )

        if trip_search_trips is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        trips_resources = [
            resources.TripSearchTripsResource.from_mongo(trip)
            for trip in trip_search_trips
        ]

        return models.JsonApiResponse(
            models.Body(
                data=trips_resources,
            ),
        )
