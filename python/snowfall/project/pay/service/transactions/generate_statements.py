import datetime
from collections.abc import Mapping, Sequence
from functools import partial
from typing import Any

import pandas as pd

from snowfall.project.junction.go.adapter import orders as orders_adapter
from snowfall.project.junction.go.adapter import (
    resellers as resellers_adapter,
)
from snowfall.project.junction.go.service.orders.v1.models_pb2 import Booking, Order
from snowfall.project.junction.go.service.resellers.v1.models_pb2 import Reseller
from snowfall.project.pay.adapter import companies, invoice_payment
from snowfall.project.pay.service.companies.v1.models_pb2 import (
    PaymentMethod,
    PaymentType,
)
from snowfall.project.pay.service.transactions.generate_csv import (
    convert_amount_to_string,
    extract_data,
    get_value,
    order_dict,
)
from snowfall.project.pay.service.transactions.transactions import (
    InvoiceRepository,
    TransactionsRepository,
)
from snowfall.project.pay.service.transactions.v1 import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout

_orders = (
    "Date Booked",
    "Booking Departure Date",
    "Traveler Forename",
    "Traveler Surname",
    "Service Fee",
    "Booking Reference",
    "Payment Method",
    "Collection Type",
)

_booking_header = {
    "Booking Departure Date": partial(
        get_value,
        key="trip_option.details.0.segment.legs.0.departure_at",
    ),
}
_order_header = {
    "Traveler Forename": partial(
        get_value,
        key="passengers.0.first_name",
    ),
    "Traveler Surname": partial(
        get_value,
        key="passengers.0.last_name",
    ),
}

_transaction_header = {
    "Date Booked": partial(get_value, key="created_at"),
    "Service Fee": partial(
        convert_amount_to_string,
        key="amounts.total_markups",
    ),
    "Booking Reference": partial(get_value, key="external_reference_id"),
    "Payment Method": partial(get_value, key="payment_method"),
    "Collection Type": partial(get_value, key="payment_type"),
}

logger = stdout.get_logger()


class StatementGenerator(object):
    def __init__(
        self,
        orders_client: orders_adapter.Client,
    ):
        self._orders_client = orders_client

    async def generate_csv(
        self,
        transactions: Sequence[models_pb2.Transaction],
    ) -> str | None:
        csv_data = await self._get_csv_data(
            transactions,
        )
        return pd.DataFrame(csv_data).to_csv()

    def report_file_path(
        self,
        reseller_name: str,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
    ) -> str:
        return "{0}/{1}_{2}.csv".format(
            reseller_name,
            from_date.date(),
            to_date.date(),
        )

    def report_name(
        self,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
    ) -> str:
        return "report_{0}_{1}.csv".format(
            from_date.date(),
            to_date.date(),
        )

    async def _get_csv_data(
        self,
        transactions: Sequence[models_pb2.Transaction],
    ) -> Sequence[Mapping[str, Any]]:
        bookings: Sequence[Booking] = (
            await self._orders_client.find_bookings(
                transaction_ids=[transaction.id for transaction in transactions],
                limit=len(transactions),
            )
        ).bookings

        orders: Sequence[Order] = (
            await self._orders_client.find_orders(
                identifiers=[booking.order_id for booking in bookings],
                limit=len(transactions),
            )
        ).orders

        return self._collect_content(
            transactions,
            bookings,
            orders,
        )

    def _collect_content(
        self,
        transactions: Sequence[models_pb2.Transaction],
        bookings: Sequence[Booking],
        orders: Sequence[Order],
    ) -> Sequence[Mapping[str, Any]]:
        bookings_map = {booking.transaction_id: booking for booking in bookings}
        orders_map = {order.id: order for order in orders}
        csv_data = []
        for transaction in transactions:
            booking = bookings_map.get(transaction.id)
            order = orders_map.get(booking.order_id) if booking else None
            row_data: dict[str, str] = {}

            extract_data(_transaction_header, transaction, row_data)
            extract_data(_booking_header, booking, row_data)
            extract_data(_order_header, order, row_data)

            csv_data.append(order_dict(_orders, row_data))

        return csv_data


class InvoiceGenerator(object):
    def __init__(
        self,
        transactions_repository: TransactionsRepository,
        invoice_repository: InvoiceRepository,
        resellers_client: resellers_adapter.GrpcClient,
        invoice_client: invoice_payment.Client,
        company_client: companies.Client,
        statement_generator: StatementGenerator,
    ):
        self._resellers_client = resellers_client
        self._transactions = transactions_repository
        self._invoice_repository = invoice_repository
        self._invoice_client = invoice_client
        self._company_client = company_client
        self._statement_generator = statement_generator

    async def generate_statements(self) -> list[tuple[str, str, str, str]]:  # noqa: WPS217, WPS231
        logger.info("Collecting resellers ...")
        resellers = await self._get_all_resellers()
        reports = []
        for reseller in resellers:
            company = await self._company_client.get(reseller.company_id)
            invoice_generation_date = protobuf.protobuf_to_date(
                company.invoice_generation_date,
            )
            invoice_generation_datetime = datetime.datetime(
                year=invoice_generation_date.year,
                month=invoice_generation_date.month,
                day=invoice_generation_date.day,
                tzinfo=datetime.UTC,
            )
            is_generation_date = (
                invoice_generation_date != datetime.datetime.now(tz=datetime.UTC).date()
            )
            if is_generation_date:
                continue

            from_date = invoice_generation_datetime - datetime.timedelta(
                days=company.invoice_generation_frequency,
            )
            logger.info("Collecting transactions ...", reseller_name=reseller.name)
            transaction_response = (
                await self._transactions.list_transactions_for_invoices(
                    filter_by_payer_ids=[company.id],
                    payment_method=PaymentMethod.PAYMENT_METHOD_INVOICE,
                    payment_type=PaymentType.PAYMENT_TYPE_CARD,
                    from_date=from_date,
                    to_date=invoice_generation_datetime,
                    invoice_id_is_not_exist=True,
                )
            )

            transactions = [transaction async for transaction in transaction_response]
            transaction_ids = [transaction.id for transaction in transactions]
            if not transaction_ids:
                continue

            csv_data = await self._statement_generator.generate_csv(transactions)
            csv_file_path = self._statement_generator.report_file_path(
                reseller.name,
                from_date,
                invoice_generation_datetime,
            )
            file_name = self._statement_generator.report_name(
                from_date,
                invoice_generation_datetime,
            )

            reports.append((
                csv_data or "",
                csv_file_path,
                company.finance_email,
                file_name,
            ))

            # TODO @Grigor: need to fix currency problem, need to configure customers in
            # the stripe to match with its default customer's currencies

            total_markups = money.total([
                money.from_protobuf(transaction.amounts.total_markups)
                for transaction in transactions
            ])

            logger.info(
                "Creating invoice ...",
                customer_id=company.payment_reference,
                amount=str(total_markups),
                currency=total_markups.currency.code,
            )
            invoice_id = await self._create_invoice(
                company.payment_reference,
                total_markups,
                company.invoice_due_days,
            )

            invoice = models_pb2.Invoice(
                id=string.uuid(),
                reseller_id=reseller.id,
                statement_path=csv_file_path,
                external_reference_id=invoice_id,
                transaction_ids=transaction_ids,
                status=models_pb2.InvoiceStatus.INVOICE_STATUS_PENDING,
            )

            await self._invoice_repository.insert(
                invoice,
            )

            await self._transactions.update_invoice_ids(
                transaction_ids,
                invoice.id,
            )

            next_invoice_generation_date = invoice_generation_date + datetime.timedelta(
                company.invoice_generation_frequency,
            )
            company.invoice_generation_date.MergeFrom(
                protobuf.date_to_protobuf(
                    next_invoice_generation_date,
                ),
            )
            company.ClearField("name")  # this is done to not get duplicate key error
            await self._company_client.update(company)

        return reports

    async def _create_invoice(
        self,
        invoice_account_id: str,
        total_markups: money.Money,
        invoice_due_days: int,
    ) -> str:
        stripe_invoice = await self._invoice_client.create_invoice(
            invoice_account_id,
            days_until_due=invoice_due_days,
        )
        await self._invoice_client.create_invoice_item(
            invoice_account_id,
            stripe_invoice.id,
            total_markups,
            description="Snowfall service fee",
        )
        await self._invoice_client.finalize_invoice(stripe_invoice.id)

        return stripe_invoice.id

    async def _get_all_resellers(self) -> Sequence[Reseller]:
        resellers_response = await self._resellers_client.list_resellers()
        resellers = list(resellers_response.resellers)
        all_resellers = resellers
        while resellers:
            resellers_response = await self._resellers_client.list_resellers(
                cursor=resellers_response.next_page_token,
            )
            resellers = list(resellers_response.resellers)
            all_resellers.extend(resellers)
        return all_resellers
