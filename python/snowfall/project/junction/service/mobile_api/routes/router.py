import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.service.mobile_api import repository
from snowfall.project.junction.service.mobile_api.routes import (  # noqa: WPS235
    enums,
    loyalty_programs,
    notification_tokens,
    offers,
    orders,
    payments,
    places,
    preferences,
    quotes,
    trips,
    user_groups,
    users,
    vouchers,
)
from snowfall.vendor.junction import client


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)
    return [
        integration.route("/places", places.Places, name="Places"),
        integration.route("/places/{placeId}", places.Place, name="ViewPlace"),
        integration.route("/orders", orders.Orders, name="ListOrders"),
        integration.route(
            "/orders/{orderId}",
            orders.Order,
            name="ViewOrder",
        ),
        integration.route(
            "/orders/{orderId}/messages",
            orders.MessageOrder,
            name="MessageOrder",
        ),
        integration.route("/offers/searches", offers.OfferSearches),
        integration.route(
            "/offers/searches/{offerSearchId}",
            offers.OfferSearch,
            name="OfferSearch",
        ),
        integration.route(
            "/offers/searches/{offerSearchId}/offers",
            offers.OffersByOfferSearch,
            name="OffersByOfferSearch",
        ),
        integration.route("/offers/quotes", quotes.OfferQuotes),
        integration.route("/offers/quotes/{offerPriceQuoteId}", quotes.OfferQuote),
        integration.route("/verification-code", users.OTPGenerate),
        integration.route("/verification-code/{userEmail}", users.OTPVerify),
        integration.route("/users/sessions", users.Session),
        integration.route("/users", users.Users),
        integration.route("/users/me", users.UserLoggedIn),
        integration.route(
            "/users/groups",
            user_groups.UserGroups,
            name="UserGroups",
        ),
        integration.route(
            "/users/groups/{groupId}",
            user_groups.UserGroup,
            name="UserGroup",
        ),
        integration.route(
            "/users/groups/{groupId}/members",
            user_groups.UserGroupMembers,
            name="UserGroupMembers",
        ),
        integration.route(
            "/users/groups/members/{memberId}",
            user_groups.UserGroupMember,
            name="UserGroupMember",
        ),
        integration.route("/users/{userEmail}", users.User),
        integration.route("/users/me/preferences", preferences.Preferences),
        integration.route("/payments", payments.Payments),
        integration.route("/payments/{paymentIntentId}", payments.Payment),
        integration.route(
            "/trips/searches/{tripSearchId}/trips",
            trips.TripSearchesTrips,
            name="TripSearchesTrips",
        ),
        integration.route("/trips/searches", trips.TripSearches, name="TripSearches"),
        integration.route(
            "/loyalty-programs",
            loyalty_programs.Programs,
            name="ListLoyaltyPrograms",
        ),
        integration.route(
            "/vouchers/{voucherCode}",
            vouchers.Voucher,
            name="Voucher",
        ),
        integration.route(
            "/push-notifications/tokens",
            notification_tokens.PushNotificationTokens,
            name="PushNotificationTokens",
        ),
        integration.route(
            "/push-notifications/tokens/{deviceToken}",
            notification_tokens.PushNotificationToken,
            name="PushNotificationToken",
        ),
        enums.CacheAndListEnum(
            dependencies[client.JunctionClient].list_cabin_classes,
            dependencies[repository.EnumsValuesRepository],
            "/cabin-classes",
        ).to_route(),
        enums.CacheAndListEnum(
            dependencies[client.JunctionClient].get_passenger_genders,
            dependencies[repository.EnumsValuesRepository],
            "/passengers/genders",
        ).to_route(),
        enums.CacheAndListEnum(
            dependencies[client.JunctionClient].get_passenger_titles,
            dependencies[repository.EnumsValuesRepository],
            "/passengers/titles",
        ).to_route(),
    ]
