import lagom
from furl import furl
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import legs as legs_adapter
from snowfall.adapter import segments as segments_adapter
from snowfall.adapter import trips as trips_adapter
from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api import models, resources
from snowfall.junction.client_api.request_helpers import sequence_paginator
from snowfall.stdlib.format import protobuf

_PAGE_LIMIT = "page[limit]"
_PAGE_CURSOR = "page[cursor]"


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
        cursor = request.query_params[_PAGE_CURSOR]
        limit = int(request.query_params[_PAGE_LIMIT])

        sequence_page = await sequence_paginator(
            sequence=models_pb2.Schedule.Type.values(),
            limit=limit,
            cursor=int(cursor) if cursor else 0,
        )

        next_url = furl(request.url_for("ListLegTypes"))
        next_url.args[_PAGE_CURSOR] = sequence_page.next_page_token
        next_url.args[_PAGE_LIMIT] = limit

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.LegTypeResource.from_proto(
                        leg_type,
                        request,
                    )
                    for leg_type in sequence_page.sequence
                ],
                links={
                    "next": next_url.url,
                },
            ),
        )


class LegsBySegmentId(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        legs_client: legs_adapter.Client = lagom.injectable,
        segments_client: segments_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        segment_id = request.path_params["segmentId"]
        try:
            segment = await segments_client.get(segment_id)
        except segments_adapter.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        try:
            legs_page = await legs_client.find_by_ids(
                segment.leg_ids,
                limit=len(segment.leg_ids),
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
            ),
        )


class LegsByTripId(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        legs_client: legs_adapter.Client = lagom.injectable,
        trips_client: trips_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        cursor = request.query_params["page[cursor]"]
        limit = int(request.query_params["page[limit]"])

        try:
            trip = await trips_client.get(request.path_params["tripId"])
        except trips_adapter.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        try:
            legs_page = await legs_client.find_by_ids(
                [leg_id for segment in trip.segments for leg_id in segment.leg_ids],
                limit=limit,
                cursor=cursor,
            )
        except legs_adapter.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        next_url = furl(
            request.url_for(
                "ListLegsByTripId",
                tripId=request.path_params["tripId"],
            ),
        )
        next_url.args["page[cursor]"] = legs_page.next_page_token
        next_url.args["page[limit]"] = limit

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.LegResource.from_proto(
                        leg=leg,
                        request=request,
                    )
                    for leg in legs_page.legs
                ],
            ),
        )
