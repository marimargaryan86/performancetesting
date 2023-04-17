import asyncio
import dataclasses
import itertools
from collections import defaultdict
from typing import Awaitable, Callable, Sequence, Type

import structlog
from starlette import requests

from snowfall.stdlib import sequence
from snowfall.stdlib.integration.starlette import models

ResolverFunc = Callable[
    [Sequence[str], requests.Request],
    Awaitable[Sequence[models.Resource]],
]


@dataclasses.dataclass(frozen=True)
class Resolver(object):
    resource: Type[models.Resource]
    func: ResolverFunc


_resolvers: dict[Type[models.Resource], Resolver] = {}
_lookup: dict[str, Type[models.Resource]] = {}


def add_resolver(resolver: Resolver) -> None:
    _lookup[resolver.resource.api_type] = resolver.resource
    _resolvers[resolver.resource] = resolver


class _IncludesResolver(object):
    def __init__(self, wanted_includes: frozenset[str]):
        self._known_resources: set[tuple[str, str]] = set()
        self._logger = structlog.get_logger(__name__)
        self._wanted_includes = wanted_includes

    async def resolve(  # noqa: WPS210
        self,
        resources: Sequence[tuple[str, models.Resource]],
        request: requests.Request,
    ) -> dict[tuple[str, str], models.Resource]:
        for _, resource in resources:
            self._known_resources.add((resource.data_type, resource.identifier))

        wanted_resources = self._find_wanted_resources(resources)
        fetched_resources_map = await self._fetch_resources(wanted_resources, request)
        resolvables = []

        for path, api_type, identifier in wanted_resources:
            try:
                resolvables.append(
                    (path, fetched_resources_map[(api_type, identifier)]),
                )
            except KeyError:
                self._logger.warning(
                    "Unable to fetch wanted resource, skipping.",
                    composite_key=(api_type, identifier),
                )

        if resolvables:
            fetched_resources_map = fetched_resources_map | await self.resolve(
                resolvables,
                request,
            )

        return fetched_resources_map

    async def _fetch_resources(  # noqa: WPS210
        self,
        relationships: frozenset[tuple[str, str, str]],
        request: requests.Request,
    ) -> dict[tuple[str, str], models.Resource]:
        identifiers_per_type: dict[str, set[str]] = defaultdict(set)
        resources: dict[tuple[str, str], models.Resource] = {}

        for _, type_key, identifier in relationships:
            identifiers_per_type[type_key].add(identifier)

        awaitables = []

        for api_type, identifiers in identifiers_per_type.items():
            try:
                awaitables.append(
                    _resolvers[_lookup[api_type]].func(
                        list(identifiers),
                        request,
                    ),
                )
            except KeyError:
                self._logger.warning(
                    "No resolver registered for type, skipping.",
                    type=api_type,
                )

        return resources | {
            (resource.data_type, resource.identifier): resource
            for resource in itertools.chain(*(await asyncio.gather(*awaitables)))
        }

    def _find_wanted_resources(  # noqa: WPS210
        self,
        resources: Sequence[tuple[str, models.Resource]],
    ) -> frozenset[tuple[str, str, str]]:
        relationships: set[tuple[str, str, str]] = set()

        for path, resource in resources:
            for rel_name, rel_data in (resource.relationships or {}).items():
                relationship_path = "{0}.{1}".format(
                    path,
                    rel_name,
                ).lstrip(".")

                if not self._is_wanted_include(relationship_path):
                    continue

                relationships = relationships.union(
                    self._to_composite_keys(
                        relationship_path,
                        sequence.ensure(rel_data["data"]),
                    ),
                )

        return frozenset(relationships)

    def _is_wanted_include(self, path: str) -> bool:
        return any(
            wanted_include
            for wanted_include in self._wanted_includes
            if wanted_include.startswith(path)
        )

    def _to_composite_keys(
        self,
        relationship_path: str,
        relationship_identifiers: Sequence[models.ResourceIdentifier],
    ) -> set[tuple[str, str, str]]:
        relationships = set()

        for relationship_identifier in relationship_identifiers:
            composite_key = (
                relationship_identifier.data_type,
                relationship_identifier.identifier,
            )

            if composite_key in self._known_resources:
                continue

            relationships.add(
                (
                    relationship_path,
                    relationship_identifier.data_type,
                    relationship_identifier.identifier,
                ),
            )

        return relationships


async def resolve_includes(
    body: models.Body,
    request: requests.Request,
) -> list[models.Resource]:
    wanted_includes = frozenset(request.scope["parsed_query_string"].get("include", []))
    resolver = _IncludesResolver(wanted_includes)

    return list(
        (
            await resolver.resolve(
                [
                    ("", resource)
                    for resource in sequence.ensure(body.resource_data)
                    if isinstance(resource, models.Resource)
                ],
                request,
            )
        ).values(),
    )
