from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.transactions.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.v1 import sort_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Bill:
        """Fetch a bill resource."""

    @abc.abstractmethod
    async def update_reconciliation(
        self,
        identifier: str,
        *,
        is_reconciled: bool,
    ) -> models_pb2.Bill:
        """Update a bill reconciliation."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        sort: sort_pb2.Sort | None = None,
    ) -> grpc_pb2.ListBillsResponse:
        """Fetch all bill resources."""


class DictClient(Client):
    def __init__(self, bills: Sequence[models_pb2.Bill]):
        self._bills = {bill.id: bill for bill in bills}

    async def get(self, bill_id: str) -> models_pb2.Bill:
        try:
            return self._bills[bill_id]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def update_reconciliation(
        self,
        identifier: str,
        *,
        is_reconciled: bool,
    ) -> models_pb2.Bill:
        bill = self._bills[identifier]
        bill.is_reconciled = is_reconciled
        self._bills[identifier] = bill

        return bill

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        sort: sort_pb2.Sort | None = None,
    ) -> grpc_pb2.ListBillsResponse:
        page = sequence.paginate(
            sequence=list(self._bills.values()),
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListBillsResponse(
            bills=page.sequence,
            next_page_token=page.cursor,
        )


class GrpcClient(Client):
    def __init__(
        self,
        bills: grpc_pb2_grpc.BillsServiceStub,
        timeout: int = 10,
    ):
        self._bills = bills
        self._timeout = timeout

    async def get(self, bill_id: str) -> models_pb2.Bill:
        response = await errors.handle_grpc_errors(
            self._bills.GetBill(
                grpc_pb2.GetBillRequest(id=bill_id),
                timeout=self._timeout,
            ),
        )

        return response.bill

    async def update_reconciliation(
        self,
        identifier: str,
        *,
        is_reconciled: bool,
    ) -> models_pb2.Bill:
        response = await errors.handle_grpc_errors(
            self._bills.UpdateBillReconciliation(
                grpc_pb2.UpdateBillReconciliationRequest(
                    id=identifier,
                    is_reconciled=is_reconciled,
                ),
                timeout=self._timeout,
            ),
        )

        return response.bill

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        sort: sort_pb2.Sort | None = None,
    ) -> grpc_pb2.ListBillsResponse:
        # TODO: handle INVALID_ARGUMENT
        request = grpc_pb2.ListBillsRequest(
            page_token=cursor or "",
            sort_by=sort,
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._bills.ListBills(request, timeout=self._timeout, sort_by=sort),
        )
