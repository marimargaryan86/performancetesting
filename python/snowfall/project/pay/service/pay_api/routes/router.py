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
    payments,
    quotations,
    rates,
    refunds,
    transactions,
)


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/transactions",
            transactions.Transactions,
            name="Transactions",
            methods=["GET", "POST"],
        ),
        integration.route(
            "/transactions/{transactionId}",
            transactions.Transaction,
            name="Transactions",
            methods=["GET"],
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
            name="Accounts",
            methods=["POST", "GET"],
        ),
        integration.route(
            "/accounts/{accountId}",
            accounts.Account,
            name="Account",
            methods=["GET", "PATCH"],
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
            methods=["POST", "GET"],
        ),
        integration.route(
            "/transactions/{transactionId}",
            transactions.Transaction,
            name="Transactions",
            methods=["GET"],
        ),
        integration.route(
            "/beneficiaries",
            beneficiaries.Beneficiaries,
            name="Beneficiaries",
        ),
        integration.route(
            "/beneficiaries/{beneficiaryId}",
            beneficiaries.Beneficiary,
            name="Beneficiary",
            methods=["GET", "PATCH"],
        ),
        integration.route(
            "/payments",
            payments.Payments,
            name="Payments",
            methods=["GET", "POST"],
        ),
        integration.route(
            "/payments/{paymentId}",
            payments.Payment,
            name="Payment",
        ),
        integration.route(
            "/refunds",
            refunds.Refunds,
            name="Refunds",
        ),
        integration.route(
            "/refunds/{refundId}",
            refunds.Refund,
            name="Refund",
            methods=["PATCH", "GET"],
        ),
        integration.route(
            "/refunds/{refundId}/refund-position",
            refunds.RefundPosition,
            name="RefundPosition",
        ),
        integration.route(
            "/refunds/bookings/{bookingId}",
            refunds.RefundByBooking,
            name="RefundByBookingId",
        ),
    ]
