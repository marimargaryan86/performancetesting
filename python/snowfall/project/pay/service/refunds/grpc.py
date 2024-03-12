import grpc

from snowfall.project.junction.go.adapter import orders as orders_adapter
from snowfall.project.junction.go.adapter.errors import NotFoundError
from snowfall.project.junction.go.service.orders.v1 import (
    models_pb2 as orders_models_pb2,
)
from snowfall.project.pay.adapter import bills as bills_adapter
from snowfall.project.pay.adapter import credit_card_payment as credit_card_adapter
from snowfall.project.pay.adapter import transactions as transactions_adapter
from snowfall.project.pay.service.companies.v1.models_pb2 import PaymentType
from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.project.pay.service.refunds import repositories
from snowfall.project.pay.service.refunds.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.transport.grpc import rich_status, service
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models.rate import (
    DetailedRateRequest,
    DetailedRateResponse,
    FixedSideEnum,
)


class RefundsService(
    service.Service,
    grpc_pb2_grpc.RefundsServiceServicer,
):
    def __init__(
        self,
        refunds: repositories.RefundsRepository,
        transactions_client: transactions_adapter.Client,
        bills_client: bills_adapter.Client,
        payment_client: PaymentClient,
        orders_client: orders_adapter.Client,
        credit_cards_client: credit_card_adapter.Client,
    ):
        self._refunds = refunds
        self._transactions_client = transactions_client
        self._payment_client = payment_client
        self._bills_client = bills_client
        self._orders_client = orders_client
        self._credit_cards_client = credit_cards_client
        self._default_page_size = 20

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["RefundsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_RefundsServiceServicer_to_server(
            self,
            server,
        )

    async def CreateRefund(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: grpc_pb2.CreateRefundRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateRefundResponse:
        try:
            await self._transactions_client.get(
                request.refund.transaction_id,
            )
        except NotFoundError:
            return await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="transaction not found",
                trailing_metadata=(
                    ("field_name", "transaction"),
                    ("field_description", "Transaction ID is not found"),
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
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetRefundResponse(refund=refund)

    async def ListRefunds(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListRefundsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListRefundsResponse:
        filters = {}
        if request.ids.ids:
            filters["_id"] = {
                "$in": list(request.ids.ids),
            }
        if request.transaction_ids.ids:
            filters["transaction_id"] = {
                "$in": list(request.transaction_ids.ids),
            }
        if request.external_reference_ids.ids:
            filters["external_reference_id"] = {
                "$in": list(request.external_reference_ids.ids),
            }
        if request.statuses:
            filters["status"] = {
                "$in": list(request.statuses),  # type: ignore[arg-type]
            }
        refunds = await self._refunds.find(
            cursor=request.page_token,
            filters=filters,
        )

        refunds.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return grpc_pb2.ListRefundsResponse(
            refunds=[refund async for refund in refunds],
            next_page_token=await refunds.cursor(),
        )

    async def UpdateRefund(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateRefundRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateRefundResponse:
        refund = await self._refunds.find_by_id(request.refund.id)
        if not refund:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        if request.refund.external_reference_id:
            updated_refund = await self._update_refund_status(context, request, refund)
            await self._update_booking_cancellation_status_success(refund)
        else:
            updated_refund = await self._execute_refund(context, request, refund)

        return grpc_pb2.UpdateRefundResponse(refund=updated_refund)

    async def CalculateRefundPosition(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: grpc_pb2.CalculateRefundPositionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CalculateRefundPositionResponse:
        refund = await self._refunds.find_by_id(request.refund_id)
        if not refund:
            return await context.abort(grpc.StatusCode.NOT_FOUND)
        try:
            transaction = await self._transactions_client.get(refund.transaction_id)
        except NotFoundError:
            return await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="transaction not found",
                trailing_metadata=(
                    ("field_name", "transaction_id"),
                    ("field_description", "Transaction ID is not found"),
                ),
            )
        await self._check_preconditions_for_refund_position(
            request.refunded_by_provider,
            request.refunded_to_reseller,
            transaction.amounts.beneficiary,
            transaction.amounts.base_converted,
            transaction.amounts.total_amount,
            context,
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

    async def UpdateRefundStatus(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: grpc_pb2.UpdateRefundStatusRequest,
        context: grpc.ServicerContext,
    ) -> grpc_pb2.UpdateRefundStatusResponse:
        is_updated = await self._refunds.update_status(
            request.external_reference_id,
            request.status,
        )
        return grpc_pb2.UpdateRefundStatusResponse(
            is_updated=is_updated,
        )

    async def _get_refund_position(
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

    async def _get_detailed_rate(
        self,
        refunded_by_provider: money_pb2.Money,
        refunded_to_reseller: money_pb2.Money,
    ) -> DetailedRateResponse:
        amount = money.from_protobuf(refunded_by_provider)
        if amount.amount < 0:
            amount = money.Money(
                amount=abs(amount.amount),
                currency=amount.currency,
            )
        if amount.amount == 0:
            amount = money.Money(
                amount=100,
                currency=amount.currency,
            )

        return await self._payment_client.get_detailed_rates(
            DetailedRateRequest(
                sell_currency=refunded_by_provider.currency_code,
                buy_currency=refunded_to_reseller.currency_code,
                fixed_side=FixedSideEnum.sell,
                amount=str(amount),
            ),
        )

    async def _update_refund_status(
        self,
        context: grpc.aio.ServicerContext,
        request: grpc_pb2.UpdateRefundRequest,
        refund: models_pb2.Refund,
    ) -> models_pb2.Refund:
        external_refund = await self._credit_cards_client.get_refund(
            request.refund.external_reference_id,
        )
        refund.MergeFrom(
            models_pb2.Refund(
                external_reference_id=request.refund.external_reference_id,
                status=models_pb2.Refund.Status.STATUS_SUCCEEDED,
                refunded_reseller=external_refund.amount,
            ),
        )
        await self._refunds.update(refund)

        return refund

    async def _update_booking_cancellation_status_success(
        self,
        refund: models_pb2.Refund,
    ) -> None:
        transaction = await self._transactions_client.get(
            identifier=refund.transaction_id,
        )
        booking_cancellation = (
            await self._orders_client.get_booking_cancellation_by_booking_id(
                booking_id=transaction.external_reference_id,
                reseller_id="",
            )
        )
        await self._orders_client.update_booking_cancellations(
            orders_models_pb2.BookingCancellation(
                id=booking_cancellation.id,
                status=orders_models_pb2.BookingCancellation.Status.STATUS_REFUND_ISSUED,
            ),
        )

    async def _execute_refund(  # noqa: WPS217
        self,
        context: grpc.aio.ServicerContext,
        request: grpc_pb2.UpdateRefundRequest,
        refund: models_pb2.Refund,
    ) -> models_pb2.Refund:
        if refund.status == models_pb2.Refund.Status.STATUS_SUBMITTED:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="status",
                    field_description="Refund already submitted",
                ),
            )

        try:
            transaction = await self._transactions_client.get(refund.transaction_id)
        except NotFoundError:
            return await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="transaction not found",
                trailing_metadata=(
                    ("field_name", "transaction"),
                    ("field_description", "Transaction ID is not found"),
                ),
            )

        await self._check_preconditions_for_refund_position(
            request.refund.refunded_us,
            request.refund.refunded_reseller,
            transaction.amounts.beneficiary,
            transaction.amounts.base_converted,
            transaction.amounts.total_amount,
            context,
        )

        detailed_rate = await self._get_detailed_rate(
            request.refund.refunded_us,
            request.refund.refunded_reseller,
        )

        refund.refund_position.CopyFrom(
            await self._get_refund_position(
                detailed_rate,
                request.refund.refunded_reseller,
                transaction.amounts.sales_margin,
                transaction.amounts.fx_margin,
                transaction.amounts.processing_margin,
            ),
        )

        if transaction.payment_type == PaymentType.PAYMENT_TYPE_CARD:
            stripe_refund = await self._create_stripe_refund(
                context,
                request,
                transaction,
            )
            refund.external_reference_id = stripe_refund.external_reference_id or ""
            refund.status = models_pb2.Refund.Status.STATUS_SUBMITTED

        refund.invoice_reference = request.refund.invoice_reference
        refund.note = request.refund.note
        refund.refund_received = request.refund.refund_received
        refund.refunded_us.CopyFrom(request.refund.refunded_us)
        refund.refunded_reseller.CopyFrom(request.refund.refunded_reseller)
        refund.refunded_us_in_payer_currency.CopyFrom(
            money.from_string(
                detailed_rate.client_buy_amount,
                money.Currency(detailed_rate.client_buy_currency),
            ).protobuf(),
        )

        return await self._refunds.update(refund)

    async def _create_stripe_refund(
        self,
        context: grpc.aio.ServicerContext,
        request: grpc_pb2.UpdateRefundRequest,
        transaction: transactions_models_pb2.Transaction,
    ) -> credit_card_models_pb2.Refund:
        try:
            bill = await self._bills_client.get(transaction.bill_id)
        except NotFoundError:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        refunded_reseller = money.from_protobuf(request.refund.refunded_reseller)

        return await self._credit_cards_client.create_refund(
            amount=refunded_reseller.amount,
            credit_card_payment_id=bill.payment_intent_id,
        )

    async def _check_preconditions_for_refund_position(
        self,
        refunded_by_provider: money_pb2.Money,
        refunded_to_reseller: money_pb2.Money,
        beneficiary: money_pb2.Money,
        base_converted: money_pb2.Money,
        total_amount: money_pb2.Money,
        context: grpc.aio.ServicerContext,
    ) -> None:
        if (  # noqa: WPS337
            refunded_by_provider.currency_code != beneficiary.currency_code
        ):
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="refunded_to_provider",
                    field_description=(
                        "Refund currencies do not match the original transaction"
                    ),
                ),
            )
        if (  # noqa: WPS337
            refunded_to_reseller.currency_code != base_converted.currency_code
        ):
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="refunded_to_reseller",
                    field_description=(
                        "Refund currencies do not match the original transaction"
                    ),
                ),
            )

        if (  # noqa: WPS337
            money.from_protobuf(refunded_to_reseller).amount
            > money.from_protobuf(total_amount).amount
        ):
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="refunded_to_reseller",
                    field_description=(
                        "Refund to reseller should not be bigger than total amount"
                    ),
                ),
            )
