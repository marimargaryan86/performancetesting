import lagom

from snowfall.project.junction.go.adapter import orders


def create_dependencies(
    orders_client: orders.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[orders.Client] = orders_client  # type: ignore[type-abstract]
    return container
