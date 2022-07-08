import datetime
from typing import cast

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.adapter import offer_searches, offers
from snowfall.project.junction.service.client_api import resources
from snowfall.project.junction.service.client_api.transformers import (
    trip_ids_to_segments,
)
from snowfall.project.junction.service.offers.v1alpha import models_pb2
from snowfall.stdlib import sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    handlers,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1alpha import models_pb2 as common_pb2


class Offer(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            offer = await client.get(request.path_params["offerId"])
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.OfferResource.from_proto(
                    offer=offer,
                    request=request,
                ),
            ),
        )


class OfferGroup(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            offer_group = await client.get_group_by_id(
                request.path_params["offerGroupId"],
            )
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.OfferGroupResource.from_proto(
                    group=offer_group,
                    request=request,
                ),
            ),
        )


class OfferGroupsByOffer(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        offer_id = request.path_params["offerId"]

        try:
            offer = await client.get(offer_id)
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=offer.groups,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.OfferGroupResource.from_proto(
                        group=group,
                        request=request,
                    )
                    for group in items_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListOfferGroupsByOffer",
                        offerId=offer_id,
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
        )


class OfferGroupDetails(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            details = await client.get_group_details_by_id(
                request.path_params["offerGroupDetailsId"],
            )
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripOfferGroupDetailsResource.from_proto(
                    segment=details,
                    request=request,
                ),
            ),
        )


class OfferGroupDetailsByOfferGroup(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        group_id = request.path_params["offerGroupId"]

        try:
            group = await client.get_group_by_id(group_id)
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=group.segments,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.TripOfferGroupDetailsResource.from_proto(
                        segment=details,
                        request=request,
                    )
                    for details in items_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListOfferGroupDetailsByOfferGroup",
                        offerGroupId=group_id,
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
        )


class OfferOption(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            option = await client.get_option_by_id(
                request.path_params["offerOptionId"],
            )
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.OfferOptionResource.from_proto(
                    option=option,
                    request=request,
                ),
            ),
        )


class OfferOptionsByOfferGroup(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        group_id = request.path_params["offerGroupId"]

        try:
            group = await client.get_group_by_id(group_id)
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=group.offers,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.OfferOptionResource.from_proto(
                        option=option,
                        request=request,
                    )
                    for option in items_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListOfferOptionsByOfferGroup",
                        offerGroupId=group_id,
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
        )


class OfferOptionDetails(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            detail = await client.get_option_details_by_id(
                request.path_params["offerOptionDetailsId"],
            )
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.OfferOptionDetailsResource.from_proto(
                    details=detail,
                    request=request,
                ),
            ),
        )


class OfferOptionDetailsByOfferOption(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        option_id = request.path_params["offerOptionId"]

        try:
            option = await client.get_option_by_id(option_id)
        except offers.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=option.segment_details,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.OfferOptionDetailsResource.from_proto(
                        details=details,
                        request=request,
                    )
                    for details in items_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListOfferOptionDetailsByOfferOption",
                        offerOptionId=option_id,
                    ),
                    items_page.cursor,
                    pagination,
                ),
            ),
        )


class OfferSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        trips_to_segments: trip_ids_to_segments.TripIdsToSegments = lagom.injectable,
        offer_search_client: offer_searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            segments = await trips_to_segments.transform(trip_ids=body["trips"])
        except trip_ids_to_segments.MissingTripsError:
            return handlers.error_response_from_status(status.HTTP_404_NOT_FOUND)

        offer_search = await offer_search_client.create(
            request=models_pb2.OfferSearch(
                trip=models_pb2.TripOfferSearch(
                    segments=segments,
                    passengers=[
                        models_pb2.Passenger(
                            date_of_birth=protobuf.date_to_protobuf(
                                datetime.date.fromisoformat(passenger["dateOfBirth"]),
                            ),
                        )
                        for passenger in body["passengers"]
                    ],
                ),
            ),
        )

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripOfferSearchResource.from_proto(
                    offer_search=offer_search,
                    offers=[],
                    request=request,
                ),
            ),
            status.HTTP_201_CREATED,
        )


class OfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offer_searches.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            offer_search = await client.get(request.path_params["offerSearchId"])
        except offer_searches.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripOfferSearchResource.from_proto(
                    offer_search=offer_search,
                    offers=[],
                    request=request,
                ),
            ),
        )


class OffersByOfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        search_client: offer_searches.Client = lagom.injectable,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        offer_search_id = request.path_params["offerSearchId"]
        cabin_classes = _get_cabin_class_filter(request)

        # todo: Check should probably be done in the RPC, but that requires refactoring.
        try:
            await search_client.get(offer_search_id)
        except offer_searches.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        pagination = pagination_helpers.get_pagination(request)
        offers_page = await client.find_offers_by_offer_search(
            identifier=offer_search_id,
            cursor=pagination.cursor,
            limit=pagination.limit,
            cabin_classes=cabin_classes,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.OfferResource.from_proto(
                        offer=offer,
                        request=request,
                    )
                    for offer in offers_page.offers
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ViewOffersByOfferSearch",
                        offerSearchId=offer_search_id,
                    ),
                    offers_page.next_page_token,
                    pagination,
                ),
            ),
        )


def _get_cabin_class_filter(
    request: requests.Request,
) -> list[common_pb2.CabinClass.Type.ValueType]:
    cabin_classes_raw = request.scope["query_string"].get(
        "filter[groups.options.details.cabinClass]",
        [],
    )

    cabin_class_enums = []

    for cabin_class_id in cabin_classes_raw:
        try:
            cabin_class_enums.append(
                protobuf.slug_to_enum_value(
                    common_pb2.CabinClass.Type.DESCRIPTOR,
                    cabin_class_id,
                ),
            )
        except KeyError:
            cabin_class_enums.append(common_pb2.CabinClass.TYPE_UNSPECIFIED)

    return [
        cast(common_pb2.CabinClass.Type.ValueType, cabin_class_enum)
        for cabin_class_enum in cabin_class_enums
    ]
