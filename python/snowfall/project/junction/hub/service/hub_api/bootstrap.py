import lagom

from snowfall.adapter import identities
from snowfall.project.junction.go.adapter import orders, resellers
from snowfall.project.junction.hub.service.hub_api import includes, repository
from snowfall.project.junction.plus.adapter import (
    configuration_vectors as config_vectors_adapter,
)
from snowfall.project.pay.adapter import (
    bills,
    companies,
    contacts,
    credit_card_payment,
    currencies,
    quotations,
    refunds,
    transactions,
)


def create_dependencies(
    orders_client: orders.Client,
    contacts_client: contacts.Client,
    companies_client: companies.Client,
    identities_client: identities.Client,
    transactions_client: transactions.Client,
    currencies_client: currencies.Client,
    quotations_client: quotations.Client,
    bills_client: bills.Client,
    refunds_client: refunds.Client,
    resellers_client: resellers.Client,
    credit_card_payment_client: credit_card_payment.Client,
    config_vectors_client: config_vectors_adapter.Client,
    users_repository: repository.UsersRepository,
) -> lagom.Container:
    container = lagom.Container()
    container[orders.Client] = orders_client  # type: ignore[type-abstract]
    container[contacts.Client] = contacts_client  # type: ignore[type-abstract]
    container[companies.Client] = companies_client  # type: ignore[type-abstract]
    container[identities.Client] = identities_client  # type: ignore[type-abstract]
    container[transactions.Client] = transactions_client  # type: ignore[type-abstract]
    container[currencies.Client] = currencies_client  # type: ignore[type-abstract]
    container[quotations.Client] = quotations_client  # type: ignore[type-abstract]
    container[bills.Client] = bills_client  # type: ignore[type-abstract]
    container[refunds.Client] = refunds_client  # type: ignore[type-abstract]
    container[resellers.Client] = resellers_client  # type: ignore[type-abstract]
    container[credit_card_payment.Client] = credit_card_payment_client  # type: ignore[type-abstract]
    container[config_vectors_adapter.Client] = config_vectors_client  # type: ignore[type-abstract]
    container[repository.UsersRepository] = users_repository

    includes.register_resolvers(
        orders_client=orders_client,
        transactions_client=transactions_client,
        refunds_client=refunds_client,
    )

    return container
