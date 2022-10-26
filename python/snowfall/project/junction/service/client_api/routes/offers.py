import datetime
from typing import Sequence, cast

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.adapter import offer_searches, offers
from snowfall.project.junction.service.client_api import resources, validators
from snowfall.project.junction.service.offers.v1alpha import models_pb2
from snowfall.stdlib import sequence, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    messages,
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
        offer = await client.get(request.path_params["offerId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.OfferResource.from_proto(
                    offer=offer,
                    request=request,
                ),
            ),
            request=request,
        )


class OfferGroup(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        offer_group = await client.get_group_by_id(
            request.path_params["offerGroupId"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.OfferGroupResource.from_proto(
                    group=offer_group,
                    request=request,
                ),
            ),
            request=request,
        )


class OfferGroupsByOffer(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        offer_id = request.path_params["offerId"]
        offer = await client.get(offer_id)
        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=offer.groups,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
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
            request=request,
        )


class OfferGroupDetails(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        details = await client.get_group_details_by_id(
            request.path_params["offerGroupDetailsId"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripOfferGroupDetailsResource.from_proto(
                    segment=details,
                    request=request,
                ),
            ),
            request=request,
        )


class OfferGroupDetailsByOfferGroup(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        group_id = request.path_params["offerGroupId"]
        group = await client.get_group_by_id(group_id)
        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=group.segments,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
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
            request=request,
        )


class OfferOption(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        option = await client.get_option_by_id(
            request.path_params["offerOptionId"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.OfferOptionResource.from_proto(
                    option=option,
                    request=request,
                ),
            ),
            request=request,
        )


class OfferOptionsByOfferGroup(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        group_id = request.path_params["offerGroupId"]
        group = await client.get_group_by_id(group_id)
        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=group.offers,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
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
            request=request,
        )


class OfferOptionDetails(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        detail = await client.get_option_details_by_id(
            request.path_params["offerOptionDetailsId"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripOfferOptionDetailsResource.from_proto(
                    details=detail,
                    request=request,
                ),
            ),
            request=request,
        )


class OfferOptionDetailsByOfferOption(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offers.Client = lagom.injectable,
    ) -> responses.Response:
        option_id = request.path_params["offerOptionId"]
        option = await client.get_option_by_id(option_id)
        pagination = pagination_helpers.get_pagination(request)
        items_page = sequence.paginate(
            sequence=option.segment_details,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.TripOfferOptionDetailsResource.from_proto(
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
            request=request,
        )


class OfferSearches(endpoints.HTTPEndpoint):
    _session_token_length = 32

    @validators.offer_search_request_validator
    async def post(
        self,
        request: requests.Request,
        offer_search_client: offer_searches.Client,
        trips_list: Sequence[common_pb2.Trip],
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        offer_search = await offer_search_client.create(
            request=models_pb2.OfferSearch(
                trip=models_pb2.TripOfferSearch(
                    trips=trips_list,
                    passengers=[
                        models_pb2.Passenger(
                            date_of_birth=protobuf.date_to_protobuf(
                                datetime.date.fromisoformat(passenger["dateOfBirth"]),
                            ),
                        )
                        for passenger in body["passengers"]
                    ],
                ),
                session_token=body.get(
                    "sessionToken",
                    string.random(self._session_token_length),
                ),
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripOfferSearchResource.from_proto(
                    offer_search=offer_search,
                    offers=[],
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )


class OfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: offer_searches.Client = lagom.injectable,
    ) -> responses.Response:
        offer_search = await client.get(request.path_params["offerSearchId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.TripOfferSearchResource.from_proto(
                    offer_search=offer_search,
                    offers=[],
                    request=request,
                ),
            ),
            request=request,
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
        await search_client.get(offer_search_id)

        pagination = pagination_helpers.get_pagination(request)
        offers_page = await client.find_offers_by_offer_search(
            identifier=offer_search_id,
            cursor=pagination.cursor,
            limit=pagination.limit,
            cabin_classes=cabin_classes,
        )

        return await messages.create_response(
            body=models.Body(
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
            request=request,
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
