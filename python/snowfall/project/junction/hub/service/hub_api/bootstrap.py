import lagom

from snowfall.project.junction.go.adapter import orders
from snowfall.project.pay.adapter import (
    accounts,
    beneficiaries,
    companies,
    contacts,
    conversions,
    currencies,
    transactions,
)
from snowfall.vendor.currency_cloud import client


def create_dependencies(  # noqa: WPS211
    orders_client: orders.Client,
    accounts_client: accounts.Client,
    contacts_client: contacts.Client,
    companies_client: companies.Client,
    conversions_client: conversions.Client,
    beneficiaries_client: beneficiaries.Client,
    transactions_client: transactions.Client,
    currencies_client: currencies.Client,
    cc_payment_client: client.PaymentClient,
) -> lagom.Container:
    container = lagom.Container()
    container[orders.Client] = orders_client  # type: ignore[type-abstract]
    container[accounts.Client] = accounts_client  # type: ignore[type-abstract]
    container[contacts.Client] = contacts_client  # type: ignore[type-abstract]
    container[companies.Client] = companies_client  # type: ignore[type-abstract]
    container[conversions.Client] = conversions_client  # type: ignore[type-abstract]
    container[beneficiaries.Client] = beneficiaries_client  # type: ignore[type-abstract]
    container[transactions.Client] = transactions_client  # type: ignore[type-abstract]
    container[currencies.Client] = currencies_client  # type: ignore[type-abstract]
    container[client.PaymentClient] = cc_payment_client

    return container
