from __future__ import annotations

import dataclasses
import datetime
import itertools
from collections.abc import Mapping, Sequence
from typing import Any, cast

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.adapter import (
    errors,
    legs,
    offer_searches,
    offers,
    price_quotes,
    trips,
)
from snowfall.project.junction.go.service.client_api import resources
from snowfall.project.junction.go.service.offers.v1alpha import models_pb2
from snowfall.project.junction.go.v1alpha import models_pb2 as common_pb2
from snowfall.stdlib import sequence, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers

_SESSION_TOKEN_LENGTH = 32
_Passengers = list[dict[str, str]]


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


@dataclasses.dataclass(frozen=True)
class OfferSearches(object):
    _legs_client: legs.Client
    _trips_client: trips.Client
    _offer_search_client: offer_searches.Client
    _reseller_currencies: Mapping[str, str]
    _reseller_pay_companies: Mapping[str, str]

    async def post(self, request: messages.Request) -> responses.Response:
        trips_list, validation_errors = await self._validate_trips(request)

        if validation_errors:
            return models.JsonApiResponse.from_errors(validation_errors)

        offer_search = await self._offer_search_client.create(
            request=await self._create_offer_search(request, trips_list),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripOfferSearchResource.from_proto(
                    offer_search=offer_search,
                    offers=[],
                    request=request.starlette_request,
                ),
            ),
            request=request.starlette_request,
            status_code=status.HTTP_201_CREATED,
        )

    async def _validate_trips(
        self,
        request: messages.Request,
    ) -> tuple[list[common_pb2.Trip], list[models.Error]]:
        body_trips = cast(list[str], request.body["trips"])
        trips_map = {
            trip.id: trip
            for trip in (
                await self._trips_client.find_by_ids(
                    body_trips,
                    limit=len(body_trips),
                )
            ).trips
        }

        return _validate_trips(
            body=request.body,
            trips_map=trips_map,
            legs_map=await self._make_legs_map(trips_map),
        )

    async def _make_legs_map(
        self,
        trips_map: Mapping[str, common_pb2.TripReference],
    ) -> dict[str, common_pb2.Leg]:
        segments = [segment for trip in trips_map.values() for segment in trip.segments]
        leg_ids = {leg_id for segment in segments for leg_id in segment.leg_ids}

        if not leg_ids:
            return {}

        return {
            leg.id: leg
            for leg in (
                await self._legs_client.find_by_ids(
                    list(leg_ids),
                    limit=len(leg_ids),
                )
            ).legs
        }

    async def _create_offer_search(
        self,
        request: messages.Request,
        trips_list: Sequence[common_pb2.Trip],
    ) -> models_pb2.OfferSearch:
        reseller_id = request.starlette_request.user.username
        offer_search = models_pb2.OfferSearch(
            reseller_id=reseller_id,
            trip=models_pb2.TripOfferSearch(
                trips=trips_list,
                passengers=[
                    models_pb2.Passenger(
                        date_of_birth=protobuf.date_to_protobuf(
                            datetime.date.fromisoformat(passenger["dateOfBirth"]),
                        ),
                    )
                    for passenger in cast(_Passengers, request.body["passengers"])
                ],
                reseller_id=reseller_id,
            ),
            session_token=cast(
                str,
                request.body.get(
                    "sessionToken",
                    string.random(_SESSION_TOKEN_LENGTH),
                ),
            ),
        )

        currency_code = self._reseller_currencies.get(reseller_id)
        company_id = self._reseller_pay_companies.get(reseller_id)

        if currency_code:
            offer_search.currency_code = currency_code

        if company_id:
            offer_search.pay_company_id = company_id

        return offer_search


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

        # TODO: Check should probably be done in the RPC, but that requires refactoring.
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


class PriceQuote(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: price_quotes.Client = lagom.injectable,
    ) -> responses.Response:
        price_quote = await client.get(request.path_params["offerPriceQuoteId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.PriceQuoteResource.from_proto(
                    price_quote=price_quote,
                    request=request,
                ),
            ),
            request=request,
        )


@dataclasses.dataclass(frozen=True)
class PriceQuotes(object):
    _offers_client: offers.Client
    _price_quotes_client: price_quotes.Client
    _reseller_pay_companies: Mapping[str, str]

    async def post(self, request: messages.Request) -> responses.Response:
        offer_id = cast(str, request.body["offer"])

        try:
            offer = await self._offers_client.get(offer_id)
        except errors.NotFoundError:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                            code="not_found",
                            detail="'{0}' was not found or has expired".format(
                                offer_id,
                            ),
                            source=models.ErrorSourcePointer(
                                pointer="/data/relationships/offer/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        option_ids = cast(list[str], request.body["options"])
        validation_errors = self._validate_options(offer, option_ids)

        if validation_errors:
            return models.JsonApiResponse(
                models.Body(errors=validation_errors),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        price_quote = await self._price_quotes_client.create(
            offer_id=offer_id,
            option_ids=option_ids,
            session_token=cast(
                str,
                request.body.get(
                    "sessionToken",
                    string.random(_SESSION_TOKEN_LENGTH),
                ),
            ),
            pay_company_id=cast(
                str,
                self._reseller_pay_companies.get(
                    request.starlette_request.user.username,
                    "",
                ),
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.PriceQuoteResource.from_proto(
                    price_quote=price_quote,
                    request=request.starlette_request,
                ),
            ),
            status_code=status.HTTP_201_CREATED,
            request=request.starlette_request,
        )

    def _validate_options(
        self,
        offer: models_pb2.OfferAggregate,
        option_ids: Sequence[str],
    ) -> list[models.Error]:
        validation_errors = [
            models.Error(
                status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                code="invalid",
                detail="'{0}' is not a valid option for this offer".format(option_id),
                source=models.ErrorSourcePointer(
                    pointer="/data/relationships/options/data/{0}/id".format(idx),
                ),
            )
            for idx, option_id in enumerate(option_ids)
            if option_id
            not in {option.id for group in offer.groups for option in group.offers}
        ]

        validation_errors.extend(self._validate_groups(offer, option_ids))

        return validation_errors

    def _validate_groups(
        self,
        offer: models_pb2.OfferAggregate,
        option_ids: Sequence[str],
    ) -> list[models.Error]:
        groups = {
            group.id: {option.id for option in group.offers} for group in offer.groups
        }

        validation_errors = [
            models.Error(
                status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                code="missing",
                detail="No option chosen for offer group '{0}'".format(group_id),
            )
            for group_id, options in groups.items()
            if not options.intersection(set(option_ids))
        ]

        validation_errors.extend(
            [
                models.Error(
                    status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                    code="duplicated_group",
                    detail="Multiple options chosen for group '{0}'".format(group_id),
                )
                for group_id, options in groups.items()
                if len(options.intersection(set(option_ids))) > 1
            ],
        )

        return validation_errors


def _get_cabin_class_filter(
    request: requests.Request,
) -> list[common_pb2.CabinClass.Type.ValueType]:
    cabin_classes_raw = request.scope["parsed_query_string"].get(
        "filter[groups.options.details.cabinClass][eq]",
        [],
    )

    cabin_class_enums: list[common_pb2.CabinClass.Type.ValueType] = []

    for cabin_class_id in cabin_classes_raw:
        try:
            cabin_class_enums.append(
                protobuf.slug_to_enum_value(
                    common_pb2.CabinClass.Type,
                    cabin_class_id,
                ),
            )
        except ValueError:
            cabin_class_enums.append(common_pb2.CabinClass.TYPE_UNSPECIFIED)

    return cabin_class_enums


def _sort_keys(segment: common_pb2.Segment) -> tuple[int, int]:
    return (
        segment.legs[0].departure_at.seconds,
        segment.legs[0].departure_at.nanos,
    )


def _validate_trips(
    body: Mapping[str, Any],
    trips_map: Mapping[str, common_pb2.TripReference],
    legs_map: Mapping[str, common_pb2.Leg],
) -> tuple[list[common_pb2.Trip], list[models.Error]]:
    trips_list: list[common_pb2.Trip] = []
    validation_errors: list[models.Error] = []

    for trip_idx, trip_id in enumerate(body["trips"]):
        if trip_id not in trips_map.keys():
            validation_errors.append(
                models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="'{0}' was not found".format(trip_id),
                    source=models.ErrorSourcePointer(
                        pointer="/data/relationships/trips/data/{0}/id".format(
                            trip_idx,
                        ),
                    ),
                ),
            )
            continue

        try:
            trips_list.append(
                common_pb2.Trip(
                    id=trip_id,
                    segments=sorted(
                        [
                            common_pb2.Segment(
                                id=segment.id,
                                legs=[legs_map[leg_id] for leg_id in segment.leg_ids],
                            )
                            for segment in trips_map[trip_id].segments
                        ],
                        key=_sort_keys,
                    ),
                ),
            )
        except KeyError:
            validation_errors.append(
                models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="'{0}' was not found".format(trip_id),
                    source=models.ErrorSourcePointer(
                        pointer="/data/relationships/trips/data/{0}/id".format(
                            trip_idx,
                        ),
                    ),
                ),
            )

    trips_list = sorted(
        trips_list,
        key=lambda trip: (
            trip.segments[0].legs[0].departure_at.seconds,  # noqa: WPS219
            trip.segments[0].legs[0].departure_at.nanos,  # noqa: WPS219
        ),
    )

    return trips_list, [*validation_errors, *_check_trip_conflicts(trips_list)]


def _check_trip_conflicts(trips_list: Sequence[common_pb2.Trip]) -> list[models.Error]:
    validation_errors = []

    for trip_a, trip_b in itertools.pairwise(trips_list):
        trip_a_arrival = trip_a.segments[-1].legs[-1].arrival_at.seconds  # noqa: WPS219
        trip_b_departure = (
            trip_b.segments[0].legs[0].departure_at.seconds  # noqa: WPS219
        )  # noqa: WPS219

        if trip_a_arrival >= trip_b_departure:
            validation_errors.append(
                models.Error(
                    status=str(status.HTTP_409_CONFLICT),
                    code="trips_conflict",
                    detail="'{0}' and '{1}' are overlapping".format(
                        trip_a.id,
                        trip_b.id,
                    ),
                    source=models.ErrorSourcePointer(
                        pointer="/data/relationships/trips",
                    ),
                ),
            )

    return validation_errors
