import contextlib
from typing import Sequence

from starlette import requests

from snowfall.project.junction.adapter import locations
from snowfall.project.junction.service.admin_api import resources
from snowfall.project.junction.service.places.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import includes


def _locations_resolver(
    locations_client: locations.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.LocationResource]:
        page = await locations_client.find(identifiers, len(identifiers))

        return [
            resources.LocationResource.from_proto(location, request)
            for location in page.locations
        ]

    return wrapper


async def _place_types_resolver(
    identifiers: Sequence[str],
    request: requests.Request,
) -> Sequence[resources.PlaceTypeResource]:
    place_types: list[resources.PlaceTypeResource] = []

    for identifier in identifiers:
        with contextlib.suppress(KeyError):
            place_types.append(
                resources.PlaceTypeResource.from_proto(
                    protobuf.slug_to_enum_value(  # type: ignore[arg-type]
                        models_pb2.Location.Type.DESCRIPTOR,
                        identifier,
                    ),
                    request,
                ),
            )

    return place_types


def register_resolvers(
    locations_client: locations.Client,
) -> None:
    resolvers = (
        includes.Resolver(
            resource=resources.LocationResource,
            func=_locations_resolver(locations_client),
        ),
        includes.Resolver(
            resource=resources.PlaceTypeResource,
            func=_place_types_resolver,
        ),
    )

    for resolver in resolvers:
        includes.add_resolver(resolver)
