import contextlib
from typing import Sequence

from starlette import requests

from snowfall.project.junction.adapter import legs, segments
from snowfall.project.junction.service.client_api import resources
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import includes
from snowfall.stdlib.v1alpha import models_pb2


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


def _segments_resolver(
    segments_client: segments.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.SegmentResource]:
        page = await segments_client.find(identifiers, len(identifiers))

        return [
            resources.SegmentResource.from_proto(location, request)
            for location in page.protos
        ]

    return wrapper


def register_resolvers(
    legs_client: legs.Client,
    segments_client: segments.Client,
) -> None:
    resolvers = (
        includes.Resolver(
            resource=resources.LegTypeResource,
            func=_leg_types_resolver,
        ),
        includes.Resolver(
            resource=resources.LegResource,
            func=_legs_resolver(legs_client),
        ),
        includes.Resolver(
            resource=resources.SegmentResource,
            func=_segments_resolver(segments_client),
        ),
    )

    for resolver in resolvers:
        includes.add_resolver(resolver)
