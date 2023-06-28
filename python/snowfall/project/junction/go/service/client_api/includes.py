import contextlib
from collections.abc import Sequence

from starlette import requests

from snowfall.project.junction.go.adapter import (
    legs,
    offers,
    orders,
    schedules,
    segments,
)
from snowfall.project.junction.go.service.client_api import resources
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import includes


async def _cabin_classes_resolver(
    identifiers: Sequence[str],
    request: requests.Request,
) -> Sequence[resources.CabinClassResource]:
    cabin_classes: list[resources.CabinClassResource] = []

    for identifier in identifiers:
        with contextlib.suppress(ValueError):
            cabin_classes.append(
                resources.CabinClassResource.from_proto(
                    protobuf.slug_to_enum_value(
                        models_pb2.CabinClass.Type,
                        identifier,
                    ),
                    request.url_for("ViewCabinClasses", enumId=identifier),
                ),
            )

    return cabin_classes


def _journeys_resolver(
    orders_client: orders.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.JourneyResource]:
        response = await orders_client.find_journeys(
            identifiers,
            limit=len(identifiers),  # noqa: WPS204
        )

        return [
            resources.JourneyResource.from_proto(journey, request)
            for journey in response.journeys
        ]

    return wrapper


def _legs_resolver(
    legs_client: legs.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.LegResource]:
        page = await legs_client.find_by_ids(identifiers, len(identifiers))

        return [
            resources.LegResource.from_proto(location, request)
            for location in page.legs
        ]

    return wrapper


async def _leg_types_resolver(
    identifiers: Sequence[str],
    request: requests.Request,
) -> Sequence[resources.LegTypeResource]:
    leg_types: list[resources.LegTypeResource] = []

    for identifier in identifiers:
        with contextlib.suppress(ValueError):
            leg_types.append(
                resources.LegTypeResource.from_proto(
                    protobuf.slug_to_enum_value(
                        models_pb2.Schedule.Type,
                        identifier,
                    ),
                    request.url_for("ViewLegsTypes", enumId=identifier),
                ),
            )

    return leg_types


def _offer_groups_resolver(
    offers_client: offers.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.OfferGroupResource]:
        page = await offers_client.find_groups_by_ids(identifiers, len(identifiers))

        return [
            resources.OfferGroupResource.from_proto(offer_group, request)
            for offer_group in page.groups
        ]

    return wrapper


def _offer_options_resolver(
    offers_client: offers.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.OfferOptionResource]:
        page = await offers_client.find_options_by_ids(identifiers, len(identifiers))

        return [
            resources.OfferOptionResource.from_proto(offer_option, request)
            for offer_option in page.options
        ]

    return wrapper


def _offers_resolver(
    offers_client: offers.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.OfferResource]:
        page = await offers_client.find_by_ids(identifiers, len(identifiers))

        return [
            resources.OfferResource.from_proto(offer, request) for offer in page.offers
        ]

    return wrapper


def _orders_resolver(
    orders_client: orders.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.OrderResource]:
        response = await orders_client.find_orders(
            identifiers,
            limit=len(identifiers),
        )

        return [
            resources.OrderResource.from_proto(order, request)
            for order in response.orders
        ]

    return wrapper


def _segments_resolver(
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.SegmentResource]:
        segments_page = await segments_client.find(identifiers, len(identifiers))
        schedule_ids = list({segment.schedule_id for segment in segments_page.segments})
        schedules_map = {
            schedule.id: schedule
            for schedule in (
                await schedules_client.find_by_ids(schedule_ids, len(schedule_ids))
            ).schedules
        }

        return [
            resources.SegmentResource.from_proto(
                segment,
                schedules_map[segment.schedule_id],
                request,
            )
            for segment in segments_page.segments
        ]

    return wrapper


def _trip_bookings_resolver(
    orders_client: orders.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.TripBookingResource]:
        response = await orders_client.find_bookings(
            identifiers,
            limit=len(identifiers),
        )

        return [
            resources.TripBookingResource.from_proto(booking, request)
            for booking in response.bookings
        ]

    return wrapper


def _trip_booking_details_resolver(
    orders_client: orders.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.TripBookingDetailsResource]:
        response = await orders_client.find_booking_details(
            identifiers,
            limit=len(identifiers),
        )

        return [
            resources.TripBookingDetailsResource.from_proto(booking_details, request)
            for booking_details in response.details
        ]

    return wrapper


def _trip_offer_group_details_resolver(
    offers_client: offers.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.TripOfferGroupDetailsResource]:
        page = await offers_client.find_group_details_by_ids(
            identifiers,
            len(identifiers),
        )

        return [
            resources.TripOfferGroupDetailsResource.from_proto(
                trip_offer_group_details,
                request,
            )
            for trip_offer_group_details in page.details
        ]

    return wrapper


def _trip_offer_option_details_resolver(
    offers_client: offers.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.TripOfferOptionDetailsResource]:
        page = await offers_client.find_option_details_by_ids(
            identifiers,
            len(identifiers),
        )

        return [
            resources.TripOfferOptionDetailsResource.from_proto(
                trip_offer_option_details,
                request,
            )
            for trip_offer_option_details in page.details
        ]

    return wrapper


def register_resolvers(
    legs_client: legs.Client,
    offers_client: offers.Client,
    segments_client: segments.Client,
    orders_client: orders.Client,
    schedules_client: schedules.Client,
) -> None:
    resolvers = (
        includes.Resolver(
            resource=resources.CabinClassResource,
            func=_cabin_classes_resolver,
        ),
        includes.Resolver(
            resource=resources.JourneyResource,
            func=_journeys_resolver(orders_client),
        ),
        includes.Resolver(
            resource=resources.LegTypeResource,
            func=_leg_types_resolver,
        ),
        includes.Resolver(
            resource=resources.LegResource,
            func=_legs_resolver(legs_client),
        ),
        includes.Resolver(
            resource=resources.OfferGroupResource,
            func=_offer_groups_resolver(offers_client),
        ),
        includes.Resolver(
            resource=resources.OfferOptionResource,
            func=_offer_options_resolver(offers_client),
        ),
        includes.Resolver(
            resource=resources.OfferResource,
            func=_offers_resolver(offers_client),
        ),
        includes.Resolver(
            resource=resources.OrderResource,
            func=_orders_resolver(orders_client),
        ),
        includes.Resolver(
            resource=resources.SegmentResource,
            func=_segments_resolver(segments_client, schedules_client),
        ),
        includes.Resolver(
            resource=resources.TripBookingDetailsResource,
            func=_trip_booking_details_resolver(orders_client),
        ),
        includes.Resolver(
            resource=resources.TripBookingResource,
            func=_trip_bookings_resolver(orders_client),
        ),
        includes.Resolver(
            resource=resources.TripOfferGroupDetailsResource,
            func=_trip_offer_group_details_resolver(offers_client),
        ),
        includes.Resolver(
            resource=resources.TripOfferOptionDetailsResource,
            func=_trip_offer_option_details_resolver(offers_client),
        ),
    )

    for resolver in resolvers:
        includes.add_resolver(resolver)
