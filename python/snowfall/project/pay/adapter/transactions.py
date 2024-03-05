from __future__ import annotations

import abc
import datetime
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.companies.v1.models_pb2 import (
    PaymentMethod,
    PaymentType,
)
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import sort_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        quotation: models_pb2.Quotation,
        external_reference: str,
        invoice_reference: str,
        order_id: str,
    ) -> models_pb2.Transaction:
        """Create a transaction resource."""

    @abc.abstractmethod
    async def get(
        self,
        identifier: str,
        selector: str | None = None,
    ) -> models_pb2.Transaction:
        """Fetch a transaction resource."""

    @abc.abstractmethod
    async def find(
        self,
        filter_by: Sequence[str] = (),
        filter_by_bill_ids: Sequence[str] = (),
        filter_by_external_reference: Sequence[str] = (),
        filter_by_payer_ids: Sequence[str] = (),
        filter_by_beneficiary_ids: Sequence[str] = (),
        filter_by_created_dates: Sequence[str] = (),
        limit: int | None = None,
        cursor: str | None = None,
        sort: sort_pb2.Sort | None = None,
    ) -> grpc_pb2.ListTransactionsResponse:
        """Fetch all transaction resources."""

    @abc.abstractmethod
    async def find_by_ids(
        self,
        fields: Sequence[str],
        selector: str = "_id",
    ) -> grpc_pb2.GetTransactionsResponse:
        """Fetch all transaction resources."""


class DictClient(Client):
    def __init__(self, transactions: Sequence[models_pb2.Transaction]) -> None:
        self._transactions = {
            transaction.id: transaction for transaction in transactions
        }

    async def create(
        self,
        quotation: models_pb2.Quotation,
        external_reference: str,
        invoice_reference: str,
        order_id: str,
    ) -> models_pb2.Transaction:
        transaction = models_pb2.Transaction(
            id=string.uuid(),
            external_reference_id=external_reference,
            invoice_reference_id=invoice_reference,
            created_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(tz=datetime.UTC),
            ),
            conversion_id=string.uuid(),
            amounts=quotation.amounts,
            rates=quotation.rates,
            payer_id=quotation.payer_id,
            beneficiary_id=quotation.beneficiary_id,
            payment_type=protobuf.slug_to_enum_value(
                PaymentType,
                "card",
            ),
            payment_method=protobuf.slug_to_enum_value(
                PaymentMethod,
                "invoice",
            ),
        )
        self._transactions[transaction.id] = transaction

        return transaction

    async def get(
        self,
        identifier: str,
        selector: str | None = None,
    ) -> models_pb2.Transaction:
        transaction = None
        if selector is None:
            transaction = self._transactions.get(identifier, None)
        else:
            for transaction_val in self._transactions.values():
                if getattr(transaction_val, selector) == identifier:
                    transaction = transaction_val
                    break
        if transaction is None:
            raise errors.NotFoundError()
        return transaction

    async def find(
        self,
        filter_by: Sequence[str] = (),
        filter_by_bill_ids: Sequence[str] = (),
        filter_by_external_reference: Sequence[str] = (),
        filter_by_payer_ids: Sequence[str] = (),
        filter_by_beneficiary_ids: Sequence[str] = (),
        filter_by_created_dates: Sequence[str] = (),
        limit: int | None = None,
        cursor: str | None = None,
        sort: sort_pb2.Sort | None = None,
    ) -> grpc_pb2.ListTransactionsResponse:
        transactions = list(self._transactions.values())
        if filter_by_external_reference:
            transactions = list(
                filter(
                    lambda transaction: transaction.external_reference_id
                    in filter_by_external_reference,
                    self._transactions.values(),
                ),
            )
        if filter_by_payer_ids:
            transactions = list(
                filter(
                    lambda transaction: transaction.payer_id in filter_by_payer_ids,
                    self._transactions.values(),
                ),
            )
        if filter_by_beneficiary_ids:
            transactions = list(
                filter(
                    lambda transaction: transaction.beneficiary_id
                    in filter_by_beneficiary_ids,
                    self._transactions.values(),
                ),
            )
        page = sequence.paginate(
            sequence=transactions,
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListTransactionsResponse(
            transactions=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_by_ids(
        self,
        fields: Sequence[str],
        selector: str = "_id",
    ) -> grpc_pb2.GetTransactionsResponse:
        transactions = []

        for field in fields:
            transaction = self._transactions.get(field)
            if transaction:
                transactions.append(transaction)

        return grpc_pb2.GetTransactionsResponse(transactions=transactions)


class GrpcClient(Client):
    def __init__(
        self,
        transactions: grpc_pb2_grpc.TransactionsServiceStub,
        timeout: int = 10,
    ):
        self._transactions = transactions
        self._timeout = timeout

    async def create(
        self,
        quotation: models_pb2.Quotation,
        external_reference: str,
        invoice_reference: str,
        order_id: str,
    ) -> models_pb2.Transaction:
        response = await errors.handle_grpc_errors(
            self._transactions.CreateTransaction(
                grpc_pb2.CreateTransactionRequest(
                    quotation=quotation,
                    external_reference=external_reference,
                    invoice_reference=invoice_reference,
                    order_id=order_id,
                ),
            ),
        )

        return response.transaction

    async def get(
        self,
        identifier: str,
        selector: str | None = None,
    ) -> models_pb2.Transaction:
        response = await errors.handle_grpc_errors(
            self._transactions.GetTransaction(
                grpc_pb2.GetTransactionRequest(id=identifier, selector=selector or ""),
                timeout=self._timeout,
            ),
        )

        return response.transaction

    async def find(
        self,
        filter_by: Sequence[str] = (),
        filter_by_bill_ids: Sequence[str] = (),
        filter_by_external_reference: Sequence[str] = (),
        filter_by_payer_ids: Sequence[str] = (),
        filter_by_beneficiary_ids: Sequence[str] = (),
        filter_by_created_dates: Sequence[str] = (),
        limit: int | None = None,
        cursor: str | None = None,
        sort: sort_pb2.Sort | None = None,
    ) -> grpc_pb2.ListTransactionsResponse:
        request = grpc_pb2.ListTransactionsRequest(
            page_token=cursor or "",
            sort_by=sort,
            filter_by=filter_by,
            filter_by_bill_ids=filter_by_bill_ids,
            filter_by_external_reference=filter_by_external_reference,
            filter_by_payer_ids=filter_by_payer_ids,
            filter_by_beneficiary_ids=filter_by_beneficiary_ids,
            filter_by_created_dates=filter_by_created_dates,
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._transactions.ListTransactions(
                request,
                timeout=self._timeout,
            ),
        )

    async def find_by_ids(
        self,
        fields: Sequence[str],
        selector: str = "_id",
    ) -> grpc_pb2.GetTransactionsResponse:
        return await errors.handle_grpc_errors(
            self._transactions.GetTransactions(
                grpc_pb2.GetTransactionsRequest(ids=fields, selector=selector),
            ),
        )
