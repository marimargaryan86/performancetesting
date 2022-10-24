from typing import Any, Awaitable, Callable, Mapping, Sequence, TypeVar

import lagom
import more_itertools
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.adapter import legs, offer_searches
from snowfall.project.junction.adapter import offers as offers_adapter
from snowfall.project.junction.adapter import orders as orders_adapter
from snowfall.project.junction.adapter import trips
from snowfall.project.junction.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.orders.v1alpha import (
    models_pb2 as order_models_pb2,
)
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.stdlib.v1alpha import models_pb2

_Endpoint = TypeVar("_Endpoint", bound=endpoints.HTTPEndpoint)

_OfferSearchEndpointSignature = Callable[
    [
        _Endpoint,
        requests.Request,
        offer_searches.Client,
        Sequence[models_pb2.Segment],
    ],
    Awaitable[responses.Response],
]

_OfferSearchValidatorSignature = Callable[
    [
        _Endpoint,
        requests.Request,
        legs.Client,
        trips.Client,
        offer_searches.Client,
    ],
    Awaitable[responses.Response],
]


def offer_search_request_validator(
    function: _OfferSearchEndpointSignature[_Endpoint],
) -> _OfferSearchValidatorSignature[_Endpoint]:
    async def wrapper(
        self: _Endpoint,
        request: requests.Request,
        legs_client: legs.Client = lagom.injectable,
        trips_client: trips.Client = lagom.injectable,
        offer_search_client: offer_searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        trips_map = {
            trip.id: trip
            for trip in (
                await trips_client.find_by_ids(
                    body["trips"],
                    limit=len(body["trips"]),
                )
            ).trips
        }

        segments = [segment for trip in trips_map.values() for segment in trip.segments]
        leg_ids = {leg_id for segment in segments for leg_id in segment.leg_ids}
        segments_and_errors = _validate_trips(
            body,
            trips_map,
            {
                leg.id: leg
                for leg in (
                    await legs_client.find_by_ids(
                        list(leg_ids),
                        limit=len(leg_ids),
                    )
                ).legs
            },
        )

        if segments_and_errors[1]:
            return models.JsonApiResponse(
                models.Body(errors=segments_and_errors[1]),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return await function(
            self,
            request,
            offer_search_client,
            segments_and_errors[0],
        )

    return wrapper


def _validate_trips(
    body: Mapping[str, Any],
    trips_map: Mapping[str, models_pb2.TripReference],
    legs_map: Mapping[str, models_pb2.Leg],
) -> tuple[list[models_pb2.Segment], list[models.Error]]:
    segments_list: list[models_pb2.Segment] = []
    errors: list[models.Error] = []

    for trip_idx, trip_id in enumerate(body["trips"]):
        if trip_id not in trips_map.keys():
            errors.append(
                models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="'{0}' was not found".format(trip_id),
                    source=models.ErrorSource(
                        pointer="/data/relationships/trips/data/{0}/id".format(
                            trip_idx,
                        ),
                    ),
                ),
            )
            continue

        try:
            segments_list.extend(
                [
                    models_pb2.Segment(
                        id=segment.id,
                        legs=[legs_map[leg_id] for leg_id in segment.leg_ids],
                    )
                    for segment in trips_map[trip_id].segments
                ],
            )
        except KeyError:
            errors.append(
                models.Error(
                    status=str(status.HTTP_404_NOT_FOUND),
                    code="not_found",
                    detail="'{0}' was not found".format(trip_id),
                    source=models.ErrorSource(
                        pointer="/data/relationships/trips/data/{0}/id".format(
                            trip_idx,
                        ),
                    ),
                ),
            )

    return segments_list, errors


def order_request_validator(  # noqa: WPS320
    function: Callable[  # noqa: WPS320
        [
            _Endpoint,
            requests.Request,
            orders_adapter.Client,
            Sequence[order_models_pb2.TripOption],
        ],
        Awaitable[responses.Response],
    ],
) -> Callable[
    [
        _Endpoint,
        requests.Request,
        offers_adapter.Client,
        orders_adapter.Client,
    ],
    Awaitable[responses.Response],
]:
    async def wrapper(
        self: _Endpoint,
        request: requests.Request,
        offers_client: offers_adapter.Client = lagom.injectable,
        orders_client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            offer = await offers_client.get(body["offer"])
        except offers_adapter.NotFoundError:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                            code="not_found",
                            detail="'{0}' was not found or has expired".format(
                                body["offer"],
                            ),
                            source=models.ErrorSource(
                                pointer="/data/relationships/offer/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        errors = _validate_options(offer, body["options"])

        if errors:
            return models.JsonApiResponse(
                models.Body(errors=errors),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        options = _create_trip_options(offer, body["options"])

        return await function(self, request, orders_client, options)

    return wrapper


def _validate_options(
    offer: offer_models_pb2.OfferAggregate,
    option_ids: Sequence[str],
) -> list[models.Error]:
    errors = [
        models.Error(
            status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
            code="invalid",
            detail="'{0}' is not a valid option for this offer".format(option_id),
            source=models.ErrorSource(
                pointer="/data/relationships/options/data/{0}/id".format(idx),
            ),
        )
        for idx, option_id in enumerate(option_ids)
        if option_id
        not in {option.id for group in offer.groups for option in group.offers}
    ]

    errors.extend(_validate_groups(offer, option_ids))

    return errors


def _validate_groups(
    offer: offer_models_pb2.OfferAggregate,
    option_ids: Sequence[str],
) -> list[models.Error]:
    groups = {
        group.id: {option.id for option in group.offers} for group in offer.groups
    }

    errors = [
        models.Error(
            status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
            code="missing",
            detail="No option chosen for offer group '{0}'".format(group_id),
        )
        for group_id, options in groups.items()
        if not options.intersection(set(option_ids))
    ]

    errors.extend(
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

    return errors


def _create_trip_options(
    offer: offer_models_pb2.OfferAggregate,
    options: Sequence[str],
) -> list[order_models_pb2.TripOption]:
    return [
        _create_trip_option(option, group)
        for group in offer.groups
        for option in group.offers
        if option.id in options
    ]


def _create_trip_option(
    option: offer_models_pb2.Offer,
    group: offer_models_pb2.OfferGroup,
) -> order_models_pb2.TripOption:
    return order_models_pb2.TripOption(
        id=option.id,
        details=[
            order_models_pb2.TripOptionDetails(
                segment=offer_segment,
                cabin_class=more_itertools.first(
                    [
                        detail.cabin_class
                        for detail in option.segment_details
                        if detail.offer_segment_id == offer_segment.id
                    ],
                ),
            )
            for offer_segment in group.segments
        ],
        price=money.from_string(
            string_amount=str(option.price.amount / 1000),
            currency=money.Currency(option.price.currency),
        ).protobuf(),
    )
