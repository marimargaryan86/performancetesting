import lagom

from snowfall.project.junction.go.adapter import orders, resellers
from snowfall.project.junction.hub.service.hub_api import includes
from snowfall.project.pay.adapter import (  # noqa: WPS235
    accounts,
    beneficiaries,
    bills,
    companies,
    contacts,
    conversions,
    currencies,
    quotations,
    refunds,
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
    quotations_client: quotations.Client,
    bills_client: bills.Client,
    refunds_client: refunds.Client,
    resellers_client: resellers.Client,
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
    container[quotations.Client] = quotations_client  # type: ignore[type-abstract]
    container[bills.Client] = bills_client  # type: ignore[type-abstract]
    container[refunds.Client] = refunds_client  # type: ignore[type-abstract]
    container[resellers.Client] = resellers_client  # type: ignore[type-abstract]

    includes.register_resolvers(transactions_client)

    return container
