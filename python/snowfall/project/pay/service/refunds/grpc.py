import grpc

from snowfall.project.junction.go.adapter.errors import NotFoundError
from snowfall.project.pay.adapter import transactions as transactions_adapter
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import PaymentType
from snowfall.project.pay.service.refunds import repositories
from snowfall.project.pay.service.refunds.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.transport.grpc import rich_status, service
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models import conversion
from snowfall.vendor.currency_cloud.models.rate import (
    DetailedRateRequest,
    DetailedRateResponse,
    FixedSideEnum,
)


class RefundsService(  # noqa: WPS214
    service.Service,
    grpc_pb2_grpc.RefundsServiceServicer,
):
    def __init__(
        self,
        refunds: repositories.RefundsRepository,
        transactions_client: transactions_adapter.Client,
        payment_client: PaymentClient,
    ):
        self._refunds = refunds
        self._transactions_client = transactions_client
        self._payment_client = payment_client
        self._default_page_size = 20

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["RefundsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_RefundsServiceServicer_to_server(
            self,
            server,
        )

    async def CreateRefund(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateRefundRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateRefundResponse:
        try:
            await self._transactions_client.get(request.refund.transaction_id)
        except NotFoundError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="transaction",
                    field_description="Transaction ID is not found",
                ),
            )

        request.refund.id = string.uuid()
        request.refund.status = models_pb2.Refund.Status.STATUS_PENDING
        refund = await self._refunds.insert(request.refund)

        return grpc_pb2.CreateRefundResponse(refund=refund)

    async def GetRefund(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetRefundRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetRefundResponse:
        refund = await self._refunds.find_by_selector(
            selection_value=request.id,
            selector=request.selector,
        )

        if not refund:
            await context.abort(grpc.StatusCode.NOT_FOUND)  # noqa: WPS204

        return grpc_pb2.GetRefundResponse(refund=refund)

    async def ListRefunds(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListRefundsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListRefundsResponse:
        refunds = await self._refunds.find(
            cursor=request.page_token,
        )

        refunds.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return grpc_pb2.ListRefundsResponse(
            refunds=[refund async for refund in refunds],
            next_page_token=await refunds.cursor(),
        )

    async def UpdateRefund(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: grpc_pb2.UpdateRefundRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateRefundResponse:
        refund = await self._refunds.find_by_id(request.refund_id)
        if not refund:
            await context.abort(grpc.StatusCode.NOT_FOUND)  # noqa: WPS204

        if (  # noqa: WPS337
            request.refunded_by_provider.currency_code
            == request.refunded_to_reseller.currency_code
        ):
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="refundedUs",
                    field_description=(
                        "refundedUs should not be same as refundedReseller"
                    ),
                ),
            )

        try:
            transaction = await self._transactions_client.get(refund.transaction_id)  # type: ignore[union-attr]
        except NotFoundError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="transaction",
                    field_description="Transaction ID is not found",
                ),
            )

        detailed_rate = await self._get_detailed_rate(
            request.refunded_by_provider,
            request.refunded_to_reseller,
        )

        refund.refund_position.CopyFrom(  # type: ignore[union-attr]
            await self._get_refund_position(
                detailed_rate,
                request.refunded_to_reseller,
                transaction.amounts.sales_margin,
                transaction.amounts.fx_margin,
                transaction.amounts.processing_margin,
            ),
        )
        conversion_id = ""
        if transaction.payment_type != PaymentType.PAYMENT_TYPE_CARD:
            cc_conversion = await self._payment_client.create_conversion(
                conversion.ConversionRequest(
                    buy_currency=request.refunded_by_provider.currency_code,
                    sell_currency=request.refunded_to_reseller.currency_code,
                    amount=str(
                        money.from_protobuf(request.refunded_by_provider),
                    ),
                    reason=transaction.id,
                ),
            )
            conversion_id = cc_conversion.identifier

        refund.status = models_pb2.Refund.Status.STATUS_EXECUTED  # type: ignore[union-attr]
        refund.conversion_id = conversion_id  # type: ignore[union-attr]
        refund.invoice_reference = request.invoice_reference  # type: ignore[union-attr]
        refund.refunded_us_in_payer_currency.CopyFrom(  # type: ignore[union-attr]
            money.from_string(
                detailed_rate.client_buy_amount,
                money.Currency(detailed_rate.client_buy_currency),
            ).protobuf(),
        )

        await self._refunds.update(refund)  # type: ignore[arg-type]

        return grpc_pb2.UpdateRefundResponse(refund=refund)

    async def CalculateRefundPosition(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: grpc_pb2.CalculateRefundPositionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CalculateRefundPositionResponse:
        refund = await self._refunds.find_by_id(request.refund_id)
        if not refund:
            await context.abort(grpc.StatusCode.NOT_FOUND)  # noqa: WPS204
        try:
            transaction = await self._transactions_client.get(refund.transaction_id)  # type: ignore[union-attr]
        except NotFoundError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="transaction_id",
                    field_description="Transactions ID is not found",
                ),
            )

        detailed_rate = await self._get_detailed_rate(
            request.refunded_by_provider,
            request.refunded_to_reseller,
        )

        refund_position = await self._get_refund_position(
            detailed_rate,
            request.refunded_to_reseller,
            transaction.amounts.sales_margin,
            transaction.amounts.fx_margin,
            transaction.amounts.processing_margin,
        )

        return grpc_pb2.CalculateRefundPositionResponse(refund_position=refund_position)

    async def _get_refund_position(  # noqa: WPS211
        self,
        detailed_rate: DetailedRateResponse,
        refunded_to_reseller: money_pb2.Money,
        sales_margin: money_pb2.Money,
        fx_margin: money_pb2.Money,
        processing_margin: money_pb2.Money,
    ) -> money_pb2.Money:
        calculated_amount = (
            money.total(
                [
                    money.from_string(
                        detailed_rate.client_buy_amount,
                        money.Currency(detailed_rate.client_buy_currency),
                    ),
                    money.from_protobuf(sales_margin),
                    money.from_protobuf(fx_margin),
                    money.from_protobuf(processing_margin),
                ],
            ).amount
            - money.from_protobuf(refunded_to_reseller).amount
        )

        return money.Money(
            calculated_amount,
            money.Currency(detailed_rate.client_buy_currency),
        ).protobuf()

    async def _get_detailed_rate(  # noqa: WPS211
        self,
        refunded_by_provider: money_pb2.Money,
        refunded_to_reseller: money_pb2.Money,
    ) -> DetailedRateResponse:
        return await self._payment_client.get_detailed_rates(
            DetailedRateRequest(
                sell_currency=refunded_by_provider.currency_code,
                buy_currency=refunded_to_reseller.currency_code,
                fixed_side=FixedSideEnum.sell,
                amount=str(money.from_protobuf(refunded_by_provider)),
            ),
        )
