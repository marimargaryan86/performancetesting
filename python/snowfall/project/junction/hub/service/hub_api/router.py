import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.hub.service.hub_api.routes import go_orders, users
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
            "/bookings/{bookingId}",
            go_orders.Booking,
            name="ViewBooking",
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
    ]
