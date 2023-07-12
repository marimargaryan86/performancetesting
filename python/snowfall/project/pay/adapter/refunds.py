from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.refunds.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.v1 import money_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(self, refund: models_pb2.Refund) -> models_pb2.Refund:
        """Create a refund resource."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Refund:
        """Fetch a refund resource."""

    @abc.abstractmethod
    async def update(
        self,
        identifier: str,
        refunded_by_provider: money_pb2.Money,
        refunded_to_reseller: money_pb2.Money,
    ) -> models_pb2.Refund:
        """Update a refund resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListRefundsResponse:
        """Fetch all refund resources."""


class DictClient(Client):
    def __init__(self, refunds: Sequence[models_pb2.Refund]):
        self._refunds = {refund.id: refund for refund in refunds}

    async def create(self, refund: models_pb2.Refund) -> models_pb2.Refund:
        self._refunds[refund.id] = refund

        return refund

    async def get(self, refund_id: str) -> models_pb2.Refund:
        try:
            return self._refunds[refund_id]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def update(
        self,
        identifier: str,
        refunded_by_provider: money_pb2.Money,
        refunded_to_reseller: money_pb2.Money,
    ) -> models_pb2.Refund:
        return self._refunds[identifier]

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListRefundsResponse:
        page = sequence.paginate(
            sequence=list(self._refunds.values()),
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListRefundsResponse(
            refunds=page.sequence,
            next_page_token=page.cursor,
        )


class GrpcClient(Client):
    def __init__(
        self,
        refunds: grpc_pb2_grpc.RefundsServiceStub,
        timeout: int = 10,
    ):
        self._refunds = refunds
        self._timeout = timeout

    async def create(self, refund: models_pb2.Refund) -> models_pb2.Refund:
        return (
            await self._refunds.CreateRefund(
                grpc_pb2.CreateRefundRequest(
                    refund=refund,
                ),
                timeout=self._timeout,
            )
        ).refund

    async def get(self, refund_id: str) -> models_pb2.Refund:
        response = await errors.handle_grpc_errors(
            self._refunds.GetRefund(
                grpc_pb2.GetRefundRequest(id=refund_id),
                timeout=self._timeout,
            ),
        )

        return response.refund

    async def update(
        self,
        identifier: str,
        refunded_by_provider: money_pb2.Money,
        refunded_to_reseller: money_pb2.Money,
    ) -> models_pb2.Refund:
        return (
            await self._refunds.UpdateRefund(
                grpc_pb2.UpdateRefundRequest(
                    refund_id=identifier,
                    refunded_by_provider=refunded_by_provider,
                    refunded_to_reseller=refunded_to_reseller,
                ),
                timeout=self._timeout,
            )
        ).refund

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListRefundsResponse:
        # TODO: handle INVALID_ARGUMENT
        request = grpc_pb2.ListRefundsRequest(
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._refunds.ListRefunds(request, timeout=self._timeout),
        )
