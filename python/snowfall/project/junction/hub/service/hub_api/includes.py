from collections.abc import Sequence

from starlette import requests

from snowfall.project.junction.go.adapter import orders
from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.pay.adapter import transactions
from snowfall.stdlib.integration.starlette import includes


def _journeys_resolver(
    orders_client: orders.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.JourneyResource]:
        response = await orders_client.find_journeys(
            identifiers,
            limit=len(identifiers),
        )

        return [
            resources.JourneyResource.from_proto(journey, request)
            for journey in response.journeys
        ]

    return wrapper


def _orders_resolver(
    orders_client: orders.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.OrderResource]:
        response = await orders_client.find_orders(
            identifiers,
            limit=len(identifiers),
        )

        return [
            resources.OrderResource.from_proto(order, request)
            for order in response.orders
        ]

    return wrapper


def _trip_bookings_resolver(
    orders_client: orders.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.TripBookingResource]:
        response = await orders_client.find_bookings(
            identifiers,
            limit=len(identifiers),
        )

        bookings_and_cancellations = (
            await orders_client.find_booking_cancellations_for_bookings(
                bookings=response.bookings,
                reseller_id=request.user.username,
            )
        )

        return [
            resources.TripBookingResource.from_proto(
                booking,
                booking_cancellation,
                request,
            )
            for booking, booking_cancellation in bookings_and_cancellations
        ]

    return wrapper


def _trip_booking_details_resolver(
    orders_client: orders.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.TripBookingDetailsResource]:
        response = await orders_client.find_booking_details(
            identifiers,
            limit=len(identifiers),
        )

        return [
            resources.TripBookingDetailsResource.from_proto(booking_details, request)
            for booking_details in response.details
        ]

    return wrapper


def _transactions_resolver(
    transactions_client: transactions.Client,
) -> includes.ResolverFunc:
    async def wrapper(
        identifiers: Sequence[str],
        request: requests.Request,
    ) -> Sequence[resources.Transaction]:
        included_transactions = []
        for identifier in identifiers:
            transaction = await transactions_client.get(identifier)
            included_transactions.append(
                resources.Transaction.from_proto(
                    transaction=transaction,
                    request=request,
                ),
            )
        return included_transactions

    return wrapper


def register_resolvers(
    orders_client: orders.Client,
    transactions_client: transactions.Client,
) -> None:
    resolvers = (
        includes.Resolver(
            resource=resources.JourneyResource,
            func=_journeys_resolver(orders_client),
        ),
        includes.Resolver(
            resource=resources.OrderResource,
            func=_orders_resolver(orders_client),
        ),
        includes.Resolver(
            resource=resources.TripBookingResource,
            func=_trip_bookings_resolver(orders_client),
        ),
        includes.Resolver(
            resource=resources.TripBookingDetailsResource,
            func=_trip_booking_details_resolver(orders_client),
        ),
        includes.Resolver(
            resource=resources.Transaction,
            func=_transactions_resolver(transactions_client),
        ),
    )
    for resolver in resolvers:
        includes.add_resolver(resolver)
