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
    CancellationRequest,
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
)
from snowfall.project.pay.service.transactions.transactions import (
    TransactionsRepository,
)
from snowfall.project.pay.service.transactions.v1.models_pb2 import Transaction
from snowfall.stdlib.format.protobuf import protobuf_to_datetime
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()
ProtoType = TypeVar("ProtoType", bound=Message)


def _get_value(
    proto_model: Message | None,
    key: str,
) -> str:
    if not proto_model:
        return ""
    proto_val: str | Message = proto_model
    for field in key.split("."):
        proto_val = getattr(proto_val, field, "")
    if isinstance(proto_val, Timestamp):
        proto_val = str(protobuf_to_datetime(proto_val))
    elif isinstance(proto_val, MutableSequence):
        proto_val = ", ".join(proto_val)
    elif isinstance(proto_val, bool):
        proto_val = "Yes" if proto_val else "No"
    return proto_val  # type: ignore[return-value]


_refunds_headers = {
    "refund_id": partial(_get_value, key="_id"),
    "transaction_id": partial(_get_value, key="transaction_id"),
    "refunded_us_in_payer_currency": partial(
        convert_amount_to_string,
        key="refunded_us_in_payer_currency",
    ),
    "refund_position": partial(convert_amount_to_string, key="refund_position"),
    "invoice_reference": partial(_get_value, key="invoice_reference"),
    "external_reference_id": partial(_get_value, key="external_reference_id"),
    "updated_at": partial(_get_value, key="updated_at"),
    "refund_received": partial(_get_value, key="refund_received"),
    "note": partial(_get_value, key="note"),
}

_transactions_headers = {
    "conversion_id": partial(_get_value, key="conversion_id"),
}

_orders_cancellation_headers = {
    "order_id": partial(_get_value, key="_id"),
    "booking_cancellations.booking_id": partial(
        _get_value,
        key="booking_cancellations.booking_id",
    ),
    "booking_cancellations.ticket_id": partial(
        _get_value,
        key="booking_cancellations.ticket_id",
    ),
    "booking_cancellations_id": partial(_get_value, key="booking_cancellations._id"),
    "created_at": partial(_get_value, key="created_at"),
}
_reseller_headers = {
    "reseller_id": partial(_get_value, key="id"),
    "reseller_name": partial(_get_value, key="name"),
    "reseller_company_id": partial(_get_value, key="company_id"),
}
_provider_headers = {
    "provider_id": partial(_get_value, key="id"),
    "provider_name": partial(_get_value, key="name"),
    "provider_company_id": partial(_get_value, key="company_id"),
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
        refunds_client: refunds_adapter.GrpcClient,
        orders_client: orders_adapter.GrpcClient,
        resellers_client: resellers_adapter.GrpcClient,
        companies_client: companies_adapter.GrpcClient,
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

    async def _get_csv_data(
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
        order_cancellations = (
            await self._orders_client.find_booking_cancellations(
                identifiers=booking_ids,
            )
        ).booking_cancellations

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
            order_cancellations,  # type: ignore[arg-type]
            providers,
            resellers,
        )

    def _collect_content(
        self,
        refunds: Sequence[Refund],
        transactions: Sequence[Transaction],
        order_cancellations: Sequence[CancellationRequest],
        providers: Sequence[Company],
        resellers: Sequence[Reseller],
    ) -> Sequence[Mapping[str, Any]]:
        transactions_map = {transaction.id: transaction for transaction in transactions}
        order_cancellations_map = {
            ord_cancel.id: ord_cancel for ord_cancel in order_cancellations
        }
        providers_map = {provider.id: provider for provider in providers}
        resellers_map = {reseller.id: reseller for reseller in resellers}

        csv_data = []
        for refund in refunds:
            transaction = transactions_map.get(refund.transaction_id)
            cancellation_req, provider, reseller = None, None, None
            if transaction:
                cancellation_req = order_cancellations_map.get(
                    transaction.external_reference_id,
                )
                provider = providers_map.get(transaction.beneficiary_id)
                reseller = resellers_map.get(transaction.payer_id)

            row_data: dict[str, str] = {}

            extract_data(_transactions_headers, transaction, row_data)
            extract_data(_refunds_headers, refund, row_data)
            extract_data(_provider_headers, provider, row_data)
            extract_data(_reseller_headers, reseller, row_data)
            extract_data(_orders_cancellation_headers, cancellation_req, row_data)

            csv_data.append(row_data)

        return csv_data
