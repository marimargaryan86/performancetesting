import lagom

from snowfall.project.junction.go.adapter import orders
from snowfall.project.pay.adapter import companies


def create_dependencies(
    orders_client: orders.Client,
    companies_client: companies.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[orders.Client] = orders_client  # type: ignore[type-abstract]
    container[companies.Client] = companies_client  # type: ignore[type-abstract]
    return container
