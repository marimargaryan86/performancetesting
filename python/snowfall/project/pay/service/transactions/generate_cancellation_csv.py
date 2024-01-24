import datetime
from collections.abc import Mapping, Sequence
from functools import partial
from typing import Any, TypeVar

import pandas as pd
from google.protobuf.message import Message

from snowfall.project.junction.go.adapter import (
    orders as orders_adapter,
)
from snowfall.project.junction.go.adapter import (
    resellers as resellers_adapter,
)
from snowfall.project.junction.go.service.orders.v1.models_pb2 import (
    Booking,
    CancellationRequest,
    Journey,
    Order,
)
from snowfall.project.junction.go.service.resellers.v1.models_pb2 import Reseller
from snowfall.project.pay.adapter import (
    companies as companies_adapter,
)
from snowfall.project.pay.adapter import (
    refunds as refunds_adapter,
)
from snowfall.project.pay.service.companies.v1.models_pb2 import Company
from snowfall.project.pay.service.refunds.v1.models_pb2 import Refund
from snowfall.project.pay.service.transactions.generate_csv import (
    convert_amount_to_string,
    extract_data,
    get_value,
    order_dict,
)
from snowfall.project.pay.service.transactions.transactions import (
    TransactionsRepository,
)
from snowfall.project.pay.service.transactions.v1.models_pb2 import Transaction
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()
ProtoType = TypeVar("ProtoType", bound=Message)

_ORDERS = (
    "Booking Departure Date",
    "Last updated",
    "Originally owed to provider",
    "Originally owed to provider Currency",
    "Refunded to us by provider",
    "Refunded to us by provider Currency",
    "Refund received",
    "Provider Name",
    "Original amount payed by reseller",
    "Original amount payed by reseller Currency",
    "Amount refunded to reseller",
    "Amount refunded to reseller Currency",
    "Reseller Name",
    "Refund Position",
    "Refund Position Currency",
    "Booking ID",
    "Zendesk ID",
    "Cancellation ID",
    "GO Order ID",
    "GO SPNR",
    "Stripe Refund Reference",
    "Payment Method",
    "Payment Type",
    "Refund Notes",
)

_refunds_headers = {
    "Refunded to us by provider": partial(
        convert_amount_to_string,
        key="refunded_us",
    ),
    "Refund received": partial(
        get_value,
        key="refund_received",
    ),
    "Amount refunded to reseller": partial(
        convert_amount_to_string,
        key="refunded_reseller",
    ),
    "Refund Position": partial(convert_amount_to_string, key="refund_position"),
    "Stripe Refund Reference": partial(get_value, key="external_reference_id"),
    "Last updated": partial(get_value, key="updated_at"),
    "Refund Notes": partial(get_value, key="note"),
}

_transactions_headers = {
    "Originally owed to provider": partial(
        convert_amount_to_string,
        key="amounts.beneficiary",
    ),
    "Original amount payed by reseller": partial(
        convert_amount_to_string,
        key="amounts.total_amount",
    ),
    "Payment Method": partial(get_value, key="payment_method"),
    "Payment Type": partial(get_value, key="payment_type"),
}

_bookings_headers = {
    "GO Order ID": partial(get_value, key="order_id"),
    "Booking Departure Date": partial(
        get_value,
        key="trip_option.details.0.segment.legs.0.departure_at",
    ),
}

_orders_cancellation_headers = {
    "Booking ID": partial(
        get_value,
        key="booking_id",
    ),
    "Zendesk ID": partial(
        get_value,
        key="ticket_id",
    ),
    "Cancellation ID": partial(get_value, key="id"),
}
_journeys_headers = {
    "GO SPNR": partial(get_value, key="passenger_name_record"),
}
_reseller_headers = {
    "Reseller Name": partial(get_value, key="name"),
}
_provider_headers = {
    "Provider Name": partial(get_value, key="name"),
}


def _extract_data(
    field_to_func: Mapping[str, partial[str]],
    db_model: Message | None,
    csv_data: dict[str, str],  # noqa: SF20
) -> None:
    for field, value_func in field_to_func.items():
        csv_data[field] = value_func(db_model)


class CSVGeneratorCancellation(object):
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        refunds_client: refunds_adapter.Client,
        orders_client: orders_adapter.Client,
        resellers_client: resellers_adapter.Client,
        companies_client: companies_adapter.Client,
    ):
        self._refunds_client = refunds_client
        self._resellers_client = resellers_client
        self._orders_client = orders_client
        self._transactions = transactions_repository
        self._companies_client = companies_client

    async def generate_csv(
        self,
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
    ) -> str | None:
        csv_data = await self._get_csv_data(
            from_date=from_date,
            to_date=to_date,
        )
        logger.info("Report is ready")
        return pd.DataFrame(csv_data).to_csv()

    def report_name(self, current_date: datetime.datetime) -> str:
        return "netsuite_cancellation_exports_{0}.csv".format(
            current_date.strftime("%d-%m-%Y"),
        )

    def report_subject(self) -> str:
        return "NetSuite cancellation export from pay"

    async def _get_csv_data(  # noqa: WPS217
        self,
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        logger.info(
            "Generating Cancellation Report: ",
            end_date=str(to_date) if to_date else "",
            start_date=str(from_date) if from_date else "",
        )

        logger.info(
            "Collecting transactions ...",
        )
        transaction_response = await self._transactions.list_transactions(
            from_date=from_date,
            to_date=to_date,
        )
        transactions = [transaction async for transaction in transaction_response]
        logger.info("Collected transactions: ", count=len(transactions))

        logger.info(
            "Collecting refunds ...",
        )
        transaction_ids = [transaction.id for transaction in transactions]
        refunds = (
            await self._refunds_client.find(
                transaction_ids=transaction_ids,
                limit=len(transaction_ids),
            )
        ).refunds

        logger.info(
            "Collecting order cancellations ...",
        )
        booking_ids = [
            transaction.external_reference_id for transaction in transactions
        ]
        booking_cancellations = (
            await self._orders_client.find_booking_cancellations(
                identifiers=booking_ids,
            )
        ).booking_cancellations

        logger.info(
            "Collecting bookings ...",
        )
        booking_cancellations_ids = {
            booking_cancellation.id for booking_cancellation in booking_cancellations
        }

        bookings = (
            await self._orders_client.find_bookings(
                identifiers=list(booking_cancellations_ids),
                limit=len(booking_cancellations_ids),
            )
        ).bookings

        logger.info("Collecting orders ...")
        bookings_ids = {booking.order_id for booking in bookings}
        orders = (
            await self._orders_client.find_orders(
                identifiers=list(bookings_ids),
                limit=len(bookings_ids),
            )
        ).orders

        logger.info("Collecting journeys ...")
        orders_ids = {order.journey_id for order in orders}
        journeys = (
            await self._orders_client.find_journeys(
                identifiers=list(orders_ids),
                limit=len(orders_ids),
            )
        ).journeys

        logger.info("Collecting resellers ...")
        reseller_ids = {transaction.payer_id for transaction in transactions}
        resellers = (
            await self._resellers_client.list_resellers(
                identifiers=list(reseller_ids),
                limit=len(reseller_ids),
            )
        ).resellers

        logger.info("Collecting providers ...")
        provider_ids = {transaction.beneficiary_id for transaction in transactions}
        providers = (
            await self._companies_client.find(
                identifiers=list(provider_ids),
                limit=len(provider_ids),
            )
        ).companies

        logger.info("Generating report ...")
        return self._collect_content(
            refunds,
            transactions,
            bookings,
            booking_cancellations,  # type: ignore[arg-type]
            providers,
            resellers,
            orders,
            journeys,
        )

    def _collect_content(
        self,
        refunds: Sequence[Refund],
        transactions: Sequence[Transaction],
        bookings: Sequence[Booking],
        booking_cancellations: Sequence[CancellationRequest],
        providers: Sequence[Company],
        resellers: Sequence[Reseller],
        orders: Sequence[Order],
        journeys: Sequence[Journey],
    ) -> Sequence[Mapping[str, Any]]:
        transactions_map = {transaction.id: transaction for transaction in transactions}
        booking_cancellations_map = {
            ord_cancel.id: ord_cancel for ord_cancel in booking_cancellations
        }
        bookings_map = {booking.id: booking for booking in bookings}
        providers_map = {provider.id: provider for provider in providers}
        resellers_map = {reseller.id: reseller for reseller in resellers}
        orders_map = {order.id: order for order in orders}
        journeys_map = {journey.id: journey for journey in journeys}

        csv_data = []
        for refund in refunds:
            transaction = transactions_map.get(refund.transaction_id)
            cancellation_req, provider, reseller, booking = None, None, None, None
            order, journey = None, None
            if transaction:
                cancellation_req = booking_cancellations_map.get(
                    transaction.external_reference_id,
                )
                provider = providers_map.get(transaction.beneficiary_id)
                reseller = resellers_map.get(transaction.payer_id)
                booking = bookings_map.get(transaction.external_reference_id)
                order = orders_map.get(booking.order_id) if booking else None
                journey = journeys_map.get(order.journey_id) if order else None

            row_data: dict[str, str] = {}

            extract_data(_transactions_headers, transaction, row_data)
            extract_data(_refunds_headers, refund, row_data)
            extract_data(_provider_headers, provider, row_data)
            extract_data(_reseller_headers, reseller, row_data)
            extract_data(_orders_cancellation_headers, cancellation_req, row_data)
            extract_data(_bookings_headers, booking, row_data)
            extract_data(_journeys_headers, journey, row_data)

            csv_data.append(order_dict(_ORDERS, row_data))

        return csv_data
