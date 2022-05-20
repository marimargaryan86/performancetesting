import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import legs as legs_adapter
from snowfall.adapter import segments as segments_adapter
from snowfall.adapter import trip_searches as trip_searches_adapter
from snowfall.adapter import trips as trips_adapter
from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api import pagination_helpers, resources
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models

_NOT_FOUND_STATUS = status.HTTP_404_NOT_FOUND


class Leg(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: legs_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            leg = await client.get(request.path_params["legId"])
        except legs_adapter.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.LegResource.from_proto(leg, request),
            ),
        )


class LegType(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        leg_type_id = request.path_params["legTypeId"]
        try:
            leg_type = protobuf.slug_to_enum_value(
                models_pb2.Schedule.Type.DESCRIPTOR,
                leg_type_id,
            )
        except KeyError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.LegTypeResource.from_proto(
                    leg_type,  # type: ignore
                    request,
                ),
            ),
        )


class LegTypes(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)

        sequence_page = pagination_helpers.sequence_paginator(
            sequence=models_pb2.Schedule.Type.values(),
            pagination=pagination,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.LegTypeResource.from_proto(
                        leg_type,
                        request,
                    )
                    for leg_type in sequence_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("ListLegTypes"),
                    sequence_page.next_page_token,
                    pagination,
                ),
            ),
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

        try:
            segment = await segments_client.get(segment_id)
        except segments_adapter.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        try:
            legs_page = await legs_client.find_by_ids(
                segment.leg_ids,
                limit=pagination.limit,
                cursor=pagination.cursor,
            )
        except legs_adapter.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
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
        )


class LegsByTripId(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        legs_client: legs_adapter.Client = lagom.injectable,
        trips_client: trips_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)

        try:
            trip = await trips_client.get(request.path_params["tripId"])
        except trips_adapter.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        try:
            legs_page = await legs_client.find_by_ids(
                [leg_id for segment in trip.segments for leg_id in segment.leg_ids],
                limit=pagination.limit,
                cursor=pagination.cursor,
            )
        except legs_adapter.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
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
        try:
            legs_page = await legs_client.find_by_ids(
                leg_ids,
                limit=pagination.limit,
                cursor=pagination.cursor,
            )
        except legs_adapter.NotFoundError:
            raise exceptions.HTTPException(_NOT_FOUND_STATUS)

        return models.JsonApiResponse(
            models.Body(
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
        )

    async def _get_all_trips(
        self,
        request: requests.Request,
        trip_searches_client: trip_searches_adapter.Client = lagom.injectable,
    ) -> list[models_pb2.TripReference]:
        trips: list[models_pb2.TripReference] = []
        trips_cursor = None
        while True:
            try:
                trips_page = await trip_searches_client.list_trips_by_trip_search(
                    request.path_params["tripSearchId"],
                    cursor=trips_cursor,
                )
            except trip_searches_adapter.NotFoundError:
                raise exceptions.HTTPException(_NOT_FOUND_STATUS)

            trips.extend(trips_page.trips)
            trips_cursor = trips_page.next_page_token

            if not trips_page.next_page_token:
                break

        return trips
