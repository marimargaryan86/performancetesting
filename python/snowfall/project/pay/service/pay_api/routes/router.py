import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.pay.service.pay_api.routes import (  # noqa: WPS235
    accounts,
    authentication,
    balances,
    companies,
    contact_persons,
    currencies,
    quotations,
    rates,
    transactions,
)


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/users/tokens",
            authentication.Authenticate,
            name="Authenticate",
            methods=["POST"],
        ),
        integration.route(
            "/users",
            authentication.CreateUser,
            name="Authenticate",
            methods=["POST"],
        ),
        integration.route(
            "/users/me",
            authentication.ChangePassword,
            name="Authenticate",
            methods=["PATCH"],
        ),
        integration.route(
            "/balances",
            balances.Balances,
            name="Balances",
        ),
        integration.route(
            "/currencies/{currencyId}",
            currencies.Currencies,
            name="Currencies",
        ),
        integration.route(
            "/transactions",
            transactions.Transactions,
            name="Transactions",
        ),
        integration.route(
            "/rates",
            rates.Rates,
            name="Rate",
        ),
        integration.route(
            "/quotes",
            quotations.Quotations,
            name="Quotation",
        ),
        integration.route(
            "/companies",
            companies.StoreCompany,
            name="Company",
        ),
        integration.route(
            "/companies/{companyId}",
            companies.StoreCompany,
            name="Company",
            methods=["PATCH"],
        ),
        integration.route(
            "/contact-persons",
            contact_persons.ContactPersons,
            name="ContactPerson",
        ),
        integration.route(
            "/accounts",
            accounts.Accounts,
            name="Account",
        ),
    ]
