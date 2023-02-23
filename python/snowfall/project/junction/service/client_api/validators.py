import itertools
from typing import Any, Awaitable, Callable, Mapping, Sequence, TypeVar

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.adapter import errors, legs, offer_searches
from snowfall.project.junction.adapter import offers as offers_adapter
from snowfall.project.junction.adapter import orders as orders_adapter
from snowfall.project.junction.adapter import price_quotes as price_quotes_adapter
from snowfall.project.junction.adapter import trips
from snowfall.project.junction.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.stdlib.v1alpha import models_pb2

_Endpoint = TypeVar("_Endpoint", bound=endpoints.HTTPEndpoint)

_OfferSearchEndpointSignature = Callable[
    [
        _Endpoint,
        requests.Request,
        offer_searches.Client,
        Sequence[models_pb2.Trip],
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

_OrderEndpointsSignature = Callable[
    [
        _Endpoint,
        requests.Request,
        price_quotes_adapter.Client,
        offers_adapter.Client,
        orders_adapter.Client,
    ],
    Awaitable[responses.Response],
]

_OrderValidatorSignature = Callable[
    [
        _Endpoint,
        requests.Request,
        price_quotes_adapter.Client,
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

        trips_list, validation_errors = _validate_trips(
            body,
            trips_map,
            await _make_legs_map(legs_client, trips_map),
        )

        if validation_errors:
            return models.JsonApiResponse.from_errors(validation_errors)

        return await function(
            self,
            request,
            offer_search_client,
            trips_list,
        )

    return wrapper


def order_request_validator(
    function: _OrderEndpointsSignature[_Endpoint],
) -> _OrderValidatorSignature[_Endpoint]:
    async def wrapper(
        self: _Endpoint,
        request: requests.Request,
        price_quotes_client: price_quotes_adapter.Client = lagom.injectable,
        offers_client: offers_adapter.Client = lagom.injectable,
        orders_client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            price_quote = await price_quotes_client.get(body["quote"])
        except errors.NotFoundError:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                            code="not_found",
                            detail="'{0}' was not found or has expired".format(
                                body["quote"],
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        validation_errors = _validate_order_request(body, price_quote)

        if validation_errors:
            return models.JsonApiResponse(
                models.Body(errors=validation_errors),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return await function(
            self,
            request,
            price_quotes_client,
            offers_client,
            orders_client,
        )

    return wrapper


def _validate_order_request(
    body: Mapping[str, Any],
    price_quote: offer_models_pb2.PriceQuoteContainer,
) -> list[models.Error]:
    validation_errors: list[models.Error] = []

    for quote in price_quote.quotes:
        validation_errors = [
            *validation_errors,
            *_validate_residence_address(
                quote.required_documents,
                body.get("residenceAddress", None),
                quote.id,
            ),
            *_validate_passport_information(
                quote.required_documents,
                body.get("passengers", None),
                quote.id,
            ),
        ]

    return validation_errors


def _validate_residence_address(
    required_fields: Sequence[Any],
    residence_address: Mapping[str, Any],
    quote_id: str,
) -> list[models.Error]:
    validation_errors: list[models.Error] = []
    req_code = offer_models_pb2.PriceQuote.Required.REQUIRED_RESIDENCE_ADDRESS

    if not residence_address and req_code in required_fields:
        return [
            _generate_mandatory_attribute_error_model(
                "residenceAddress",
                quote_id,
            ),
        ]

    if req_code in required_fields:
        residence_address_attributes = [
            "addressLines",
            "postalCode",
            "countryCode",
            "city",
        ]

        for attr in residence_address_attributes:
            if not residence_address or not residence_address.get(attr):
                validation_errors.append(
                    _generate_mandatory_attribute_error_model(
                        "residenceAddress.{0}".format(
                            attr,
                        ),
                        quote_id,
                    ),
                )

    return validation_errors


def _validate_passport_information(  # noqa: WPS210
    required_fields: Sequence[Any],
    passengers: Sequence[Any],
    quote_id: str,
) -> list[models.Error]:
    validation_errors: list[models.Error] = []
    passport_attributes: list[tuple[int, str]] = [
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_DATE_OF_BIRTH,
            "dateOfBirth",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_NATIONALITY,
            "nationality",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_EXPIRATION_DATE,
            "documentExpirationDate",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_ISSUING_COUNTRY,
            "documentIssueCountry",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_PASSPORT_NUMBER,
            "documentNumber",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_PASSPORT_NUMBER,
            "documentType",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_RESIDENCE_COUNTRY_CODE,
            "residenceCountryCode",
        ),
    ]

    for index, passenger in enumerate(passengers):
        doc = passenger.get("travelerDocument")
        for attribute in passport_attributes:
            doc_attribute_is_not_present = doc is None or doc.get(attribute[1]) is None

            if attribute[0] in required_fields and doc_attribute_is_not_present:
                validation_errors.append(
                    _generate_mandatory_attribute_error_model(
                        "passengers[{0}].travelerDocument.{1}".format(
                            index,
                            attribute[1],
                        ),
                        quote_id,
                    ),
                )

    return validation_errors


def _generate_mandatory_attribute_error_model(
    error_message: str,
    quote_id: str,
) -> models.Error:
    return models.Error(
        status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
        code="invalid",
        detail="'{0}' attribute is mandatory for quote '{1}'".format(
            error_message,
            quote_id,
        ),
        source=models.ErrorSource(
            pointer="/data/relationships/quote/data/id",
        ),
    )


async def _make_legs_map(
    legs_client: legs.Client,
    trips_map: Mapping[str, models_pb2.TripReference],
) -> dict[str, models_pb2.Leg]:
    segments = [segment for trip in trips_map.values() for segment in trip.segments]
    leg_ids = {leg_id for segment in segments for leg_id in segment.leg_ids}

    if not leg_ids:
        return {}

    return {
        leg.id: leg
        for leg in (
            await legs_client.find_by_ids(
                list(leg_ids),
                limit=len(leg_ids),
            )
        ).legs
    }


def _sort_keys(segment: models_pb2.Segment) -> tuple[int, int]:
    return (
        segment.legs[0].departure_at.seconds,
        segment.legs[0].departure_at.nanos,
    )


def _validate_trips(
    body: Mapping[str, Any],
    trips_map: Mapping[str, models_pb2.TripReference],
    legs_map: Mapping[str, models_pb2.Leg],
) -> tuple[list[models_pb2.Trip], list[models.Error]]:
    trips_list: list[models_pb2.Trip] = []
    validation_errors: list[models.Error] = []

    for trip_idx, trip_id in enumerate(body["trips"]):
        if trip_id not in trips_map.keys():
            validation_errors.append(
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
            trips_list.append(
                models_pb2.Trip(
                    id=trip_id,
                    segments=sorted(
                        [
                            models_pb2.Segment(
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
                    source=models.ErrorSource(
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

    return _check_trip_conflicts(trips_list, validation_errors)


def _check_trip_conflicts(
    trips_list: list[models_pb2.Trip],  # noqa: SF20
    validation_errors: list[models.Error],  # noqa: SF20
) -> tuple[list[models_pb2.Trip], list[models.Error]]:
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
                    source=models.ErrorSource(pointer="/data/relationships/trips"),
                ),
            )

    return trips_list, validation_errors


def price_quote_request_validator(  # noqa: WPS320
    function: Callable[  # noqa: WPS320
        [
            _Endpoint,
            requests.Request,
            price_quotes_adapter.Client,
            Sequence[str],
        ],
        Awaitable[responses.Response],
    ],
) -> Callable[
    [
        _Endpoint,
        requests.Request,
        offers_adapter.Client,
        price_quotes_adapter.Client,
    ],
    Awaitable[responses.Response],
]:
    async def wrapper(
        self: _Endpoint,
        request: requests.Request,
        offers_client: offers_adapter.Client = lagom.injectable,
        price_quotes_client: price_quotes_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            offer = await offers_client.get(body["offer"])
        except errors.NotFoundError:
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

        validation_errors = _validate_options(offer, body["options"])

        if validation_errors:
            return models.JsonApiResponse(
                models.Body(errors=validation_errors),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return await function(self, request, price_quotes_client, body["options"])

    return wrapper


def _validate_options(
    offer: offer_models_pb2.OfferAggregate,
    option_ids: Sequence[str],
) -> list[models.Error]:
    validation_errors = [
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

    validation_errors.extend(_validate_groups(offer, option_ids))

    return validation_errors


def _validate_groups(
    offer: offer_models_pb2.OfferAggregate,
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
