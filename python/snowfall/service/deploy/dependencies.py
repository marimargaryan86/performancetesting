from __future__ import annotations

import asyncio
import dataclasses
import pathlib
from collections import defaultdict
from collections.abc import Mapping, Sequence

import aiofiles

from snowfall.stdlib.format import hcl2


@dataclasses.dataclass(frozen=True)
class Resolver:
    _dependency_lookup: Mapping[str, frozenset[str]]
    _service_dependencies: Mapping[str, frozenset[str]]

    def get_transitive_dependencies_for(
        self,
        service: str,
        skip: Sequence[str] | None = None,
    ) -> frozenset[str]:
        dependencies = self._dependency_lookup.get(service, frozenset()).copy()
        if skip is None:
            skip = []
        for providing_service in self._dependency_lookup.get(service, []):
            for dependency in self._service_dependencies.get(providing_service, []):
                if dependency in skip:
                    continue
                skip = [*skip, dependency]
                dependencies = dependencies.union(
                    self.get_transitive_dependencies_for(dependency, skip),
                )

        return frozenset(dependencies)


@dataclasses.dataclass(frozen=True)
class _ResolvedTemplate:
    service: str
    needs: frozenset[str] = dataclasses.field(default_factory=frozenset)
    provides: frozenset[str] = dataclasses.field(default_factory=frozenset)


async def resolver_from_nomad_templates(
    templates_path: pathlib.Path,
) -> Resolver:
    dependency_lookup = defaultdict(set)
    service_dependencies = defaultdict(set)
    resolved_templates: Sequence[_ResolvedTemplate] = await asyncio.gather(
        *[
            _resolve_from_nomad_template(nomad_template)
            for nomad_template in templates_path.glob("**/*.nomad")
        ],
    )

    for resolved_template in resolved_templates:
        for provided in resolved_template.provides:
            dependency_lookup[provided].add(resolved_template.service)

        for needed in resolved_template.needs:
            service_dependencies[resolved_template.service].add(needed)

    return Resolver(
        _dependency_lookup={
            dependency: frozenset(services)
            for dependency, services in dependency_lookup.items()
        },
        _service_dependencies={
            service: frozenset(dependencies)
            for service, dependencies in service_dependencies.items()
        },
    )


async def _resolve_from_service(
    service: hcl2.Service,
    job_name: str,
) -> tuple[frozenset[str], frozenset[str]]:
    needs: set[str] = set()
    provides: set[str] = set()

    for connect in service.connect:
        for sidecar in connect.sidecar_service:
            provides.add(
                service.name.removesuffix(
                    "-${var.environment}",
                ).replace("${JOB}", job_name),
            )

            for proxy in sidecar.proxy:
                needs.update(
                    upstream.destination_name.removesuffix(
                        "-${var.environment}",
                    )
                    for upstream in proxy.upstreams
                )

    return frozenset(needs), frozenset(provides)


async def _resolve_from_job(
    job: hcl2.Job,
    job_name: str,
) -> tuple[frozenset[str], frozenset[str]]:
    needs: set[str] = set()
    provides: set[str] = set()

    for group_map in job.group:
        for group in group_map.values():
            for service in group.service:
                new_needs, new_provides = await _resolve_from_service(
                    service,
                    job_name,
                )

                needs = needs.union(new_needs)
                provides = provides.union(new_provides)

    return frozenset(needs), frozenset(provides)


async def _resolve_from_nomad_template(
    template_path: pathlib.Path,
) -> _ResolvedTemplate:
    async with aiofiles.open(template_path) as template_file:
        template = hcl2.loads(await template_file.read())

    needs: set[str] = set()
    provides: set[str] = set()

    for job_map in template.job:
        for job_name, job in job_map.items():
            new_needs, new_provides = await _resolve_from_job(
                job,
                job_name,
            )

            needs = needs.union(new_needs)
            provides = provides.union(new_provides)

    return _ResolvedTemplate(
        service=template_path.parent.name,
        needs=frozenset(needs),
        provides=frozenset(provides),
    )
