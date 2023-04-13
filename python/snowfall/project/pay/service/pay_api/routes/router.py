import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.pay.service.pay_api.routes import (  # noqa: WPS235
    accounts,
    authentication,
    balances,
    beneficiaries,
    companies,
    contacts,
    conversions,
    currencies,
    quotations,
    rates,
    transactions,
)


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/currencies",
            currencies.ListCurrencies,
            name="Currencies",
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
    ]


def get_admin_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
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
            "/companies",
            companies.AdminCompanies,
            name="Companies",
        ),
        integration.route(
            "/companies/accountless",
            companies.AdminAccountlessCompanies,
            name="AccountlessCompanies",
        ),
        integration.route(
            "/companies/{companyId}",
            companies.AdminCompany,
            name="Company",
            methods=["PATCH", "GET"],
        ),
        integration.route(
            "/companies/{companyId}/contacts",
            contacts.Contacts,
            name="Contact",
        ),
        integration.route(
            "/accounts",
            accounts.Accounts,
            name="Account",
            methods=["POST", "GET"],
        ),
        integration.route(
            "/conversions/{conversionId}",
            conversions.Conversions,
            name="Conversion",
        ),
        integration.route(
            "/conversions",
            conversions.ListConversions,
            name="ListConversion",
            methods=["GET"],
        ),
        integration.route(
            "/accounts/{accountId}/balances",
            balances.Balances,
            name="Balances",
            methods=["GET"],
        ),
        integration.route(
            "/accounts/{accountId}/relationships/currencies",
            balances.Balances,
            name="Balances",
            methods=["POST"],
        ),
        integration.route(
            "/transactions",
            transactions.Transactions,
            name="Transactions",
            methods=["POST"],
        ),
        integration.route(
            "/transactions/{transactionId}",
            transactions.Transactions,
            name="Transactions",
            methods=["GET"],
        ),
        integration.route(
            "/transactions",
            transactions.ListTransactions,
            name="ListTransactions",
        ),
        integration.route(
            "/beneficiaries",
            beneficiaries.Beneficiaries,
            name="Beneficiaires",
        ),
    ]
