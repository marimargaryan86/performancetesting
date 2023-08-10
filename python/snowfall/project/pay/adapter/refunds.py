from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.refunds.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transaction_model,
)
from snowfall.stdlib import money, sequence
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models.rate import (
    DetailedRateRequest,
    FixedSideEnum,
)


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Refund:
        """Fetch a refund resource."""

    @abc.abstractmethod
    async def update(
        self,
        identifier: str,
        refunded_by_provider: money_pb2.Money,
        refunded_to_reseller: money_pb2.Money,
        invoice_reference: str,
    ) -> models_pb2.Refund:
        """Update a refund resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListRefundsResponse:
        """Fetch all refund resources."""

    @abc.abstractmethod
    async def calculate_refund_position(
        self,
        refund_id: str,
        refunded_by_provider: money.Money,
        refunded_to_reseller: money.Money,
    ) -> money.Money:
        """Calculate refund position."""


class DictClient(Client):
    def __init__(
        self,
        refunds: Sequence[models_pb2.Refund],
        transactions: Sequence[transaction_model.Transaction],
        payment_client: PaymentClient,
    ):
        self._refunds = {refund.id: refund for refund in refunds}
        self._transactions = {
            transaction.id: transaction for transaction in transactions
        }
        self._payment_client = payment_client

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
        invoice_reference: str,
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

    async def calculate_refund_position(
        self,
        refund_id: str,
        refunded_by_provider: money.Money,
        refunded_to_reseller: money.Money,
    ) -> money.Money:
        refund = self._refunds.get(refund_id)
        if not refund:
            raise errors.NotFoundError("Refund not found")
        transaction = self._transactions.get(refund.transaction_id)
        if not transaction:
            raise errors.NotFoundError("Transaction not found")
        detailed_rate_response = await self._payment_client.get_detailed_rates(
            DetailedRateRequest(
                sell_currency=refunded_by_provider.currency.code,
                buy_currency=refunded_to_reseller.currency.code,
                fixed_side=FixedSideEnum.sell,
                amount=str(refunded_by_provider.amount),
            ),
        )
        total_amount = money.total(
            [
                money.Money(
                    int(detailed_rate_response.client_buy_amount),
                    money.Currency(refunded_to_reseller.currency.code),
                ),
                money.from_protobuf(transaction.amounts.sales_margin),
                money.from_protobuf(transaction.amounts.fx_margin),
                money.from_protobuf(transaction.amounts.processing_margin),
            ],
        ).amount

        calculated_amount = total_amount - refunded_to_reseller.amount
        return money.Money(
            calculated_amount,
            money.Currency(refunded_to_reseller.currency.code),
        )


class GrpcClient(Client):
    def __init__(
        self,
        refunds: grpc_pb2_grpc.RefundsServiceStub,
        timeout: int = 10,
    ):
        self._refunds = refunds
        self._timeout = timeout

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
        invoice_reference: str,
    ) -> models_pb2.Refund:
        return (
            await self._refunds.UpdateRefund(
                grpc_pb2.UpdateRefundRequest(
                    refund_id=identifier,
                    refunded_by_provider=refunded_by_provider,
                    refunded_to_reseller=refunded_to_reseller,
                    invoice_reference=invoice_reference,
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

    async def calculate_refund_position(
        self,
        refund_id: str,
        refunded_by_provider: money.Money,
        refunded_to_reseller: money.Money,
    ) -> money.Money:
        refund_position_response = await errors.handle_grpc_errors(
            self._refunds.CalculateRefundPosition(
                grpc_pb2.CalculateRefundPositionRequest(
                    refund_id=refund_id,
                    refunded_by_provider=refunded_by_provider.protobuf(),
                    refunded_to_reseller=refunded_to_reseller.protobuf(),
                ),
            ),
        )
        return money.from_protobuf(refund_position_response.refund_position)
