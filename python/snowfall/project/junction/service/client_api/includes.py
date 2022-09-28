import contextlib
from typing import Sequence

from starlette import requests

from snowfall.project.junction.adapter import legs, offers, segments
from snowfall.project.junction.service.client_api import resources
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import includes
from snowfall.stdlib.v1alpha import models_pb2


async def _cabin_classes_resolver(
    identifiers: Sequence[str],
    request: requests.Request,
) -> Sequence[resources.CabinClassResource]:
    cabin_classes: list[resources.CabinClassResource] = []

    for identifier in identifiers:
        with contextlib.suppress(KeyError):
            cabin_classes.append(
                resources.CabinClassResource.from_proto(
                    protobuf.slug_to_enum_value(  # type: ignore[arg-type]
                        models_pb2.CabinClass.Type.DESCRIPTOR,
                        identifier,
                    ),
                    request,
                ),
            )

    return cabin_classes


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
        with contextlib.suppress(KeyError):
            leg_types.append(
                resources.LegTypeResource.from_proto(
                    protobuf.slug_to_enum_value(  # type: ignore[arg-type]
                        models_pb2.Schedule.Type.DESCRIPTOR,
                        identifier,
                    ),
                    request,
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
            for offer_group in page.protos
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
            for offer_option in page.protos
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


def _segments_resolver(
    segments_client: segments.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.SegmentResource]:
        page = await segments_client.find(identifiers, len(identifiers))

        return [
            resources.SegmentResource.from_proto(segment, request)
            for segment in page.protos
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
            for trip_offer_group_details in page.protos
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
            for trip_offer_option_details in page.protos
        ]

    return wrapper


def register_resolvers(
    legs_client: legs.Client,
    offers_client: offers.Client,
    segments_client: segments.Client,
) -> None:
    resolvers = (
        includes.Resolver(
            resource=resources.CabinClassResource,
            func=_cabin_classes_resolver,
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
            resource=resources.SegmentResource,
            func=_segments_resolver(segments_client),
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
