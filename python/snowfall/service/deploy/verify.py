from collections.abc import Sequence

from snowfall.service.deploy import consul
from snowfall.service.deploy.verifiers import protocols
from snowfall.stdlib.logging import stdout


async def _resolve_dependencies(
    resolver: consul.Resolver,
    dependencies: protocols.Dependencies,
) -> protocols.ResolvedDependencies:
    resolved = {}

    for dependency in dependencies:
        resolved[dependency] = await resolver.query_service(dependency)

    return resolved


async def run(
    verifier: protocols.Verifier,
    environment: str,
    changed_services: Sequence[str],
    logger: stdout.Logger,
    resolver: consul.Resolver,
) -> bool:
    with stdout.context_binding(verifier=type(verifier).__name__):
        is_triggered = any(srv in verifier.triggers for srv in changed_services)

        if not is_triggered or environment not in verifier.environments:
            logger.warning("Skipped due to environments or triggers not matching.")
            return True

        try:
            resolved_dependencies = await _resolve_dependencies(
                resolver,
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
