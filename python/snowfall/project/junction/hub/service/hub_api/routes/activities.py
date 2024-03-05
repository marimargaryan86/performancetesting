import contextlib
from collections.abc import Sequence

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.go.adapter import orders as orders_adapter
from snowfall.project.junction.go.adapter import resellers as resellers_adapter
from snowfall.project.junction.go.service.orders.v1.models_pb2 import (
    Booking,
    Journey,
    Order,
)
from snowfall.project.junction.go.service.resellers.v1.models_pb2 import Reseller
from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.project.pay.adapter import (
    companies as companies_adapter,
)
from snowfall.project.pay.adapter import (
    transactions as transactions_adapter,
)
from snowfall.project.pay.service.companies.v1.models_pb2 import Company
from snowfall.project.pay.service.transactions.v1.models_pb2 import Transaction
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
)
from snowfall.stdlib.v1 import sort_pb2


class Activity(endpoints.HTTPEndpoint):
    async def get(  # noqa: WPS217
        self,
        request: requests.Request,
        transactions_client: transactions_adapter.Client = lagom.injectable,
        orders_client: orders_adapter.Client = lagom.injectable,
        companies_client: companies_adapter.Client = lagom.injectable,
        resellers_client: resellers_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        transaction_id = request.path_params["transactionId"]

        transaction = await transactions_client.get(transaction_id)
        bookings = await orders_client.find_bookings(transaction_ids=[transaction.id])
        booking = bookings.bookings[0]
        order = await orders_client.get_order(booking.order_id)
        journey = await orders_client.get_journey(order.journey_id)

        reseller = await resellers_client.get_reseller(
            journey.reseller_id,
        )
        company = await companies_client.get(reseller.company_id)
        activity_resource = None
        with contextlib.suppress(Exception):
            activity_resource = resources.ActivityResource.from_proto(
                transaction,
                order,
                booking,
                company,
                reseller,
                request,
            )
        if not activity_resource:
            raise exceptions.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return await messages.create_response(
            body=models.Body(
                data=activity_resource,
            ),
            request=request,
        )


class Activities(endpoints.HTTPEndpoint):
    async def get(  # noqa: WPS217
        self,
        request: requests.Request,
        transactions_client: transactions_adapter.Client = lagom.injectable,
        orders_client: orders_adapter.Client = lagom.injectable,
        companies_client: companies_adapter.Client = lagom.injectable,
        resellers_client: resellers_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        filter_transaction_created_date = request.query_params.get(
            "filter[transactionCreatedDates][eq]",
        )
        filter_beneficiaries_ids = request.query_params.get(
            "filter[beneficiaryIds][eq]",
        )
        filter_payers_ids = request.query_params.get(
            "filter[payerIds][eq]",
        )
        transaction_created_dates, payer_ids, beneficiary_ids = [], [], []
        if filter_transaction_created_date:
            transaction_created_dates = filter_transaction_created_date.split(",")
        if filter_beneficiaries_ids:
            beneficiary_ids = filter_beneficiaries_ids.split(",")
        if filter_payers_ids:
            payer_ids = filter_payers_ids.split(",")

        transaction_response = await transactions_client.find(
            limit=pagination.limit,
            cursor=pagination.cursor,
            filter_by_payer_ids=payer_ids,
            filter_by_beneficiary_ids=beneficiary_ids,
            filter_by_created_dates=transaction_created_dates,
            sort=sort_pb2.Sort(
                field="created_at",
                order=sort_pb2.Sort.ORDER_DESCENDING,
            ),
        )
        transactions = transaction_response.transactions

        filter_departure_dates = request.query_params.get(
            "filter[departureDates][eq]",
        )
        departure_dates = (
            filter_departure_dates.split(",") if filter_departure_dates else []
        )

        bookings = (
            await orders_client.find_bookings(
                transaction_ids=[transaction.id for transaction in transactions],
                limit=len(transactions),
                filter_by_departure_dates=departure_dates,
            )
        ).bookings

        filter_by_order_ids = request.query_params.get("filter[orderIds][eq]")

        if filter_by_order_ids:
            order_ids = filter_by_order_ids.split(",")
        else:
            order_ids = [booking.order_id for booking in bookings]

        orders = (
            await orders_client.find_orders(
                identifiers=order_ids,
                limit=len(order_ids),
            )
        ).orders

        journeys = (
            await orders_client.find_journeys(
                identifiers=[order.journey_id for order in orders],
                limit=len(orders),
            )
        ).journeys

        journey_reseller_ids = {journey.reseller_id for journey in journeys}
        resellers = (
            await resellers_client.list_resellers(
                identifiers=list(journey_reseller_ids),
                limit=len(journey_reseller_ids),
            )
        ).resellers

        provider_ids = {reseller.company_id for reseller in resellers}

        companies = (
            await companies_client.find(
                identifiers=list(provider_ids),
                limit=len(provider_ids),
            )
        ).companies

        response = self._collect_content(
            transactions,
            bookings,
            companies,
            orders,
            journeys,
            resellers,
            request,
        )

        return await messages.create_response(
            body=models.Body(
                data=response,
                links=pagination_helpers.get_next_url(
                    request.url_for("Activities"),
                    transaction_response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )

    def _collect_content(  # noqa: WPS231
        self,
        transactions: Sequence[Transaction],
        bookings: Sequence[Booking],
        companies: Sequence[Company],
        orders: Sequence[Order],
        journeys: Sequence[Journey],
        resellers: Sequence[Reseller],
        request: requests.Request,
    ) -> Sequence[resources.ActivityResource]:
        bookings_map = {booking.transaction_id: booking for booking in bookings}
        orders_map = {order.id: order for order in orders}
        companies_map = {company.id: company for company in companies}
        journeys_map = {journey.id: journey for journey in journeys}
        resellers_map = {reseller.id: reseller for reseller in resellers}
        json_data = []
        for transaction in transactions:
            booking = bookings_map.get(transaction.id)
            order = orders_map.get(booking.order_id) if booking else None
            journey = journeys_map.get(order.journey_id) if order else None
            reseller = resellers_map.get(journey.reseller_id) if journey else None
            company = companies_map.get(reseller.company_id) if reseller else None

            if booking and order and reseller and company:
                with contextlib.suppress(Exception):
                    json_data.append(
                        resources.ActivityResource.from_proto(
                            transaction,
                            order,
                            booking,
                            company,
                            reseller,
                            request,
                        ),
                    )

        return json_data
