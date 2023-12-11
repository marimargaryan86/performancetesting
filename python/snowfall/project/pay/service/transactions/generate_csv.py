import datetime
from collections.abc import Mapping, MutableSequence, Sequence
from functools import partial
from typing import Any, TypeVar

import pandas as pd
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp

from snowfall.project.junction.go.adapter import (
    orders as orders_adapter,
)
from snowfall.project.junction.go.adapter import (
    resellers as resellers_adapter,
)
from snowfall.project.junction.go.service.orders.v1.models_pb2 import (
    Booking,
    Journey,
    Order,
)
from snowfall.project.junction.go.service.resellers.v1.models_pb2 import Reseller
from snowfall.project.pay.adapter import (
    companies as companies_adapter,
)
from snowfall.project.pay.service.companies.v1 import models_pb2
from snowfall.project.pay.service.transactions.transactions import (
    TransactionsRepository,
)
from snowfall.project.pay.service.transactions.v1.models_pb2 import Transaction
from snowfall.stdlib import money
from snowfall.stdlib.format.protobuf import enum_value_to_slug, protobuf_to_datetime
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.v1.money_pb2 import Money

logger = stdout.get_logger()
ProtoType = TypeVar("ProtoType", bound=Message)


def _convert_amount_to_string(
    proto_model: Message | None,
    key: str,
) -> tuple[str, str]:
    if not proto_model:
        return "", ""
    proto_val: Message | Money | str = proto_model
    for field in key.split("."):
        proto_val = getattr(proto_val, field, "")
    try:
        money_value = money.from_protobuf(proto_val)  # type: ignore[arg-type]
    except ValueError:
        return "", ""
    return str(money_value), money_value.currency.code


def _get_value(  # noqa: WPS231
    proto_model: Message | None,
    key: str,
) -> str:
    if not proto_model:
        return ""

    if key == "lead_reseller_markup":
        return "0"
    if key == "payment_method":
        return enum_value_to_slug(
            models_pb2.PaymentMethod.DESCRIPTOR,
            getattr(proto_model, key, 0),
        )
    if key == "payment_type":
        return enum_value_to_slug(
            models_pb2.PaymentType.DESCRIPTOR,
            getattr(proto_model, key, 0),
        )
    proto_val: str | Message = proto_model
    for field in key.split("."):
        if field.isdigit():
            index = int(field)
            proto_val = proto_val[index] if index < len(proto_val) else ""  # type: ignore[arg-type,index]
        else:
            proto_val = getattr(proto_val, field, "")
    if isinstance(proto_val, Timestamp):
        proto_val = str(protobuf_to_datetime(proto_val))
    elif isinstance(proto_val, MutableSequence):
        proto_val = ", ".join(proto_val)
    return proto_val  # type: ignore[return-value]


class CSVGenerator(object):
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        orders_client: orders_adapter.GrpcClient,
        resellers_client: resellers_adapter.GrpcClient,
        companies_client: companies_adapter.GrpcClient,
    ):
        self._transaction_header = {
            "Date Booked": partial(_get_value, key="created_at"),
            "Base Fare in reseller currency": partial(
                _convert_amount_to_string,
                key="amounts.base_converted",
            ),
            "Sales Fee": partial(
                _convert_amount_to_string,
                key="amounts.sales_margin",
            ),
            "FX Fee": partial(
                _convert_amount_to_string,
                key="amounts.fx_margin",
            ),
            "Acquiring Fee": partial(
                _convert_amount_to_string,
                key="amounts.processing_margin",
            ),
            "Total Fees": partial(
                _convert_amount_to_string,
                key="amounts.total_markups",
            ),
            "Offer Without Tax": partial(
                _convert_amount_to_string,
                key="amounts.quotation",
            ),
            "Tax in Reseller currency": partial(
                _convert_amount_to_string,
                key="amounts.tax_converted",
            ),
            "Reseller Owes Snowfall": partial(
                _convert_amount_to_string,
                key="amounts.total_amount",
            ),
            "Snowfall Owes Provider": partial(
                _convert_amount_to_string,
                key="amounts.beneficiary",
            ),
            # TODO: Fixed Fee
            "Provider Reference": partial(_get_value, key="invoice_reference_id"),
            "GO Booking ID": partial(_get_value, key="external_reference_id"),
            "Payment Method": partial(_get_value, key="payment_method"),
            "Payment Type": partial(_get_value, key="payment_type"),
            "Sales Fee Percentage": partial(_get_value, key="rates.fx_markup"),
            "FX Fee Percentage": partial(_get_value, key="rates.sales_markup"),
            "Acquiring Fee Percentage": partial(
                _get_value,
                key="rates.processing_markup",
            ),
        }
        self._bookings_headers = {
            "GO Order ID": partial(_get_value, key="order_id"),
            "Booking Departure Date": partial(
                _get_value,
                key="trip_option.details.0.segment.legs.0.departure_at",
            ),
        }
        self._journeys_headers = {
            "GO SPNR": partial(_get_value, key="passenger_name_record"),
        }
        self._reseller_headers = {
            "Reseller Name": partial(_get_value, key="name"),
        }
        self._company_headers = {
            "Provider Name": partial(_get_value, key="name"),
        }
        self._transactions = transactions_repository
        self._orders_client = orders_client
        self._resellers_client = resellers_client
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

    async def _get_csv_data(  # noqa: WPS217
        self,
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        logger.info(
            "Generating Report: ",
            end_date=str(to_date) if to_date else "",
            start_date=str(from_date) if from_date else "",
        )
        logger.info("Collecting transactions ...")
        transaction_response = await self._transactions.list_transactions(
            from_date=from_date,
            to_date=to_date,
        )
        transactions = [transaction async for transaction in transaction_response]
        logger.info("Transactions number", count=len(transactions))

        logger.info("Collecting bookings ...")
        bookings: Sequence[Booking] = (
            await self._orders_client.find_bookings(
                transaction_ids=[transaction.id for transaction in transactions],
                limit=len(transactions),
            )
        ).bookings

        logger.info("Collecting orders ...")
        orders: Sequence[Order] = (
            await self._orders_client.find_orders(
                identifiers=[booking.order_id for booking in bookings],
                limit=len(transactions),
            )
        ).orders

        logger.info("Collecting journeys ...")
        journeys: Sequence[Journey] = (
            await self._orders_client.find_journeys(
                identifiers=[order.journey_id for order in orders],
                limit=len(transactions),
            )
        ).journeys

        logger.info("Collecting resellers ...")
        journeys_resellers_ids = {journey.reseller_id for journey in journeys}
        resellers: Sequence[Reseller] = (
            await self._resellers_client.list_resellers(
                identifiers=list(journeys_resellers_ids),
                limit=len(journeys_resellers_ids),
            )
        ).resellers

        logger.info("Collecting companies ...")
        provider_ids = [reseller.company_id for reseller in resellers]

        companies = (
            await self._companies_client.find(
                identifiers=provider_ids,
                limit=len(provider_ids),
            )
        ).companies

        logger.info("Generating report ...")
        return self._collect_content(
            transactions,
            bookings,
            companies,  # type: ignore[arg-type]
            orders,
            journeys,
            resellers,
        )

    def _collect_content(
        self,
        transactions: Sequence[Transaction],
        bookings: Sequence[Booking],
        companies: Sequence[Order],
        orders: Sequence[Order],
        journeys: Sequence[Journey],
        resellers: Sequence[Reseller],
    ) -> Sequence[Mapping[str, Any]]:
        bookings_map = {booking.transaction_id: booking for booking in bookings}
        orders_map = {order.id: order for order in orders}
        companies_map = {company.id: company for company in companies}
        journeys_map = {journey.id: journey for journey in journeys}
        resellers_map = {reseller.id: reseller for reseller in resellers}
        csv_data = []
        for transaction in transactions:
            booking = bookings_map.get(transaction.id)
            order = orders_map.get(booking.order_id) if booking else None
            journey = journeys_map.get(order.journey_id) if order else None
            reseller = resellers_map.get(journey.reseller_id) if journey else None
            company = companies_map.get(reseller.company_id) if reseller else None

            row_data: dict[str, str] = {}

            self._extract_data(self._transaction_header, transaction, row_data)
            self._extract_data(self._bookings_headers, booking, row_data)
            self._extract_data(self._company_headers, company, row_data)
            self._extract_data(self._journeys_headers, journey, row_data)
            self._extract_data(self._reseller_headers, reseller, row_data)

            csv_data.append(row_data)

        return csv_data

    def _extract_data(
        self,
        field_to_func: Mapping[str, Any],
        db_model: Message | None,
        csv_data: dict[str, str],  # noqa: SF20
    ) -> None:
        for field, value_func in field_to_func.items():
            if value_func.func == _convert_amount_to_string:
                values = value_func(db_model)
                csv_data[field] = values[0]
                csv_data[field + " Currency"] = values[1]  # noqa: WPS336
            else:
                csv_data[field] = value_func(db_model)
