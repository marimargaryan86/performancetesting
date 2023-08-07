import functools
import itertools
from collections.abc import Sequence

from snowfall.service.deploy import consul, dependencies
from snowfall.service.deploy.verifiers import protocols
from snowfall.stdlib.logging import stdout


@functools.cache
def _logger() -> stdout.Logger:
    return stdout.get_logger()


async def _resolve_dependencies(
    resolver: consul.Resolver,
    service_dependencies: protocols.Dependencies,
) -> protocols.ResolvedDependencies:
    resolved = {}

    for dependency in service_dependencies:
        resolved[dependency] = await resolver.query_service(dependency)

    return resolved


async def run(
    verifier: protocols.Verifier,
    environment: str,
    changed_services: Sequence[str],
    dns_resolver: consul.Resolver,
    deps_resolver: dependencies.Resolver,
) -> bool:
    logger = _logger()

    with stdout.context_binding(verifier=type(verifier).__name__):
        triggers = frozenset(
            itertools.chain(
                *[
                    deps_resolver.get_transitive_dependencies_for(dependency[0])
                    for dependency in verifier.dependencies
                ],
            ),
        )

        is_triggered = any(srv in triggers for srv in changed_services)

        if not is_triggered or environment not in verifier.environments:
            logger.warning("Skipped due to environments or triggers not matching.")
            return True

        try:
            resolved_dependencies = await _resolve_dependencies(
                dns_resolver,
                verifier.dependencies,
            )
        except Exception:
            logger.exception(
                "Unable to resolve verifier dependencies.",
                dependency=verifier.dependencies,
            )
            return False

        try:
            await verifier.run(environment, resolved_dependencies)
        except Exception:
            logger.exception("Verifier failed.")
            return False

        logger.info("Verifier passed.")
        return True
