import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.hub.service.hub_api.routes import (
    accounts,
    companies,
    contacts,
    go_orders,
    users,
)
from snowfall.stdlib.integration.starlette import routes


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    user_handler = users.Users()

    return [
        routes.to_route(
            "/users",
            user_handler.list_,
            name="ListUsers",
        ),
        routes.to_route(
            "/users/{userId}",
            user_handler.view,
            name="ViewUser",
        ),
        integration.route(
            "/orders/{orderId}/bookings",
            go_orders.BookingsByOrder,
            name="ListBookingsByOrder",
        ),
        integration.route(
            "/bookings/cancellations",
            go_orders.BookingsCancellation,
            name="CreateBookingsCancellation",
        ),
        integration.route(
            "/bookings/cancellations/{bookingsCancellationId}",
            go_orders.BookingsCancellation,
            name="ViewBookingsCancellation",
        ),
        integration.route(
            "/bookings/{bookingId}",
            go_orders.Booking,
            name="ViewBooking",
        ),
        integration.route(
            "/bookings/{bookingId}/cancellation",
            go_orders.BookingsCancellationByBooking,
            name="ViewBookingCancellationByBooking",
        ),
        integration.route(
            "/bookings/{bookingId}/details",
            go_orders.DetailsByBooking,
            name="ListDetailsByBooking",
        ),
        integration.route(
            "/bookings/details/{bookingDetailsId}",
            go_orders.BookingDetails,
            name="ViewBookingDetails",
        ),
        integration.route(
            "/journeys/{journeyId}",
            go_orders.Journey,
            name="ViewJourney",
        ),
        integration.route(
            "/journeys",
            go_orders.Journeys,
            name="ListJourneys",
        ),
        integration.route(
            "/journeys/{journeyId}/orders",
            go_orders.OrdersByJourney,
            name="ListOrdersByJourney",
        ),
        integration.route(
            "/orders/{orderId}",
            go_orders.Order,
            name="ViewOrder",
        ),
        integration.route(
            "/accounts",
            accounts.Accounts,
            name="Accounts",
            methods=["GET", "POST"],
        ),
        integration.route(
            "/accounts/{accountId}",
            accounts.Account,
            name="Account",
            methods=["GET", "PATCH"],
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
    ]
