import lagom

from snowfall.project.junction.go.adapter import orders
from snowfall.project.pay.adapter import (
    accounts,
    companies,
    contacts,
)
from snowfall.vendor.currency_cloud import client


def create_dependencies(
    orders_client: orders.Client,
    accounts_client: accounts.Client,
    contacts_client: contacts.Client,
    companies_client: companies.Client,
    cc_payment_client: client.PaymentClient,
) -> lagom.Container:
    container = lagom.Container()
    container[orders.Client] = orders_client  # type: ignore[type-abstract]
    container[accounts.Client] = accounts_client  # type: ignore[type-abstract]
    container[contacts.Client] = contacts_client  # type: ignore[type-abstract]
    container[companies.Client] = companies_client  # type: ignore[type-abstract]
    container[client.PaymentClient] = cc_payment_client

    return container
