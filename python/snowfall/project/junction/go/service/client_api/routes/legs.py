import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.adapter import legs as legs_adapter
from snowfall.project.junction.go.adapter import segments as segments_adapter
from snowfall.project.junction.go.adapter import trip_searches as trip_searches_adapter
from snowfall.project.junction.go.adapter import trips as trips_adapter
from snowfall.project.junction.go.service.client_api import resources
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers

_NOT_FOUND_STATUS = status.HTTP_404_NOT_FOUND


class Leg(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: legs_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        leg = await client.get(request.path_params["legId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.LegResource.from_proto(leg, request),
            ),
            request=request,
        )


class LegsBySegmentId(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        legs_client: legs_adapter.Client = lagom.injectable,
        segments_client: segments_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        segment_id = request.path_params["segmentId"]
        segment = await segments_client.get(segment_id)
        legs_page = await legs_client.find_by_ids(
            segment.leg_ids,
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.LegResource.from_proto(
                        leg=leg,
                        request=request,
                    )
                    for leg in legs_page.legs
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListLegsBySegmentId",
                        segmentId=segment_id,
                    ),
                    legs_page.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )


class LegsByTripId(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        legs_client: legs_adapter.Client = lagom.injectable,
        trips_client: trips_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        trip = await trips_client.get(request.path_params["tripId"])
        legs_page = await legs_client.find_by_ids(
            [leg_id for segment in trip.segments for leg_id in segment.leg_ids],
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.LegResource.from_proto(
                        leg=leg,
                        request=request,
                    )
                    for leg in legs_page.legs
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListLegsByTripId",
                        tripId=request.path_params["tripId"],
                    ),
                    legs_page.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )


class LegsByTripSearchId(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        trip_searches_client: trip_searches_adapter.Client = lagom.injectable,
        legs_client: legs_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        trips = await self._get_all_trips(request, trip_searches_client)
        segments = [segment for trip in trips for segment in trip.segments]
        leg_ids = [leg_id for segment in segments for leg_id in segment.leg_ids]

        if not leg_ids:
            return await messages.create_response(
                body=models.Body(
                    data=[],
                    links={
                        "next": str(request.url),
                    },
                ),
                request=request,
            )

        legs_page = await legs_client.find_by_ids(
            leg_ids,
            limit=pagination.limit,
            cursor=pagination.cursor,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.LegResource.from_proto(
                        leg=leg,
                        request=request,
                    )
                    for leg in legs_page.legs
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListLegsByTripSearchId",
                        tripSearchId=request.path_params["tripSearchId"],
                    ),
                    legs_page.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )

    async def _get_all_trips(
        self,
        request: requests.Request,
        trip_searches_client: trip_searches_adapter.Client,
    ) -> list[models_pb2.TripReference]:
        trips: list[models_pb2.TripReference] = []
        trips_cursor = None

        while True:
            trips_page = await trip_searches_client.list_trips_by_trip_search(
                request.path_params["tripSearchId"],
                cursor=trips_cursor,
            )
            trips.extend(trips_page.trips)
            trips_cursor = trips_page.next_page_token

            if not trips_page.trips:
                break

        return trips
