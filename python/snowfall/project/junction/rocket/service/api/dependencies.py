import lagom

from snowfall.project.junction.rocket.adapter import (
    search_results as search_results_adapter,
)
from snowfall.project.junction.rocket.adapter import (
    searches as searches_adapter,
)


def create_dependencies(
    search_results_client: search_results_adapter.Client,
    searches_client: searches_adapter.Client,
) -> lagom.Container:
    container = lagom.Container()

    container[search_results_adapter.Client] = search_results_client  # type: ignore[type-abstract]
    container[searches_adapter.Client] = searches_client  # type: ignore[type-abstract]

    return container
