import types
from typing import cast

import grpc

from snowfall.project.junction.go.adapter import errors as adapter_errors
from snowfall.project.pay.adapter import companies, credit_card_payment, currencies
from snowfall.project.pay.service.transactions.cache import UserSessionRepository
from snowfall.project.pay.service.transactions.quote import Quote
from snowfall.project.pay.service.transactions.transactions import (
    BillsRepository,
    InvoiceRepository,
    QuotationsRepository,
    TransactionsRepository,
)
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.transport.grpc import rich_status, service, sorting
from snowfall.stdlib.v1 import money_pb2

_TRANSACTION_STATUS_MAPPING = types.MappingProxyType({
    models_pb2.InvoiceStatus.INVOICE_STATUS_SUCCEEDED: models_pb2.TransactionStatus.TRANSACTION_STATUS_SUCCEEDED,
    models_pb2.InvoiceStatus.INVOICE_STATUS_FAILED: models_pb2.TransactionStatus.TRANSACTION_STATUS_FAILED,
})


class TransactionsService(
    service.Service,
    grpc_pb2_grpc.TransactionsServiceServicer,
):
    def __init__(
        self,
        transactions: TransactionsRepository,
        quotations: QuotationsRepository,
        bills: BillsRepository,
        companies_client: companies.Client,
        invoices: InvoiceRepository,
        credit_card_client: credit_card_payment.Client,
    ):
        self._transactions = transactions
        self._quotations = quotations
        self._invoices = invoices
        self._bills = bills
        self._companies = companies_client
        self._sort = {"created_at": "created_at"}
        self._default_page_size = 20
        self._credit_card_client = credit_card_client

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["TransactionsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_TransactionsServiceServicer_to_server(
            self,
            server,
        )

    async def ListTransactions(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListTransactionsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListTransactionsResponse:
        transactions = await self._transactions.list_transactions(
            cursor=request.page_token,
            sort=sorting.get_sort(request.sort_by, self._sort),
            filter_by_ids=request.filter_by,
            filter_by_bill_ids=request.filter_by_bill_ids,
            filter_by_external_reference=request.filter_by_external_reference,
            filter_by_payer_ids=request.filter_by_payer_ids,
            filter_by_beneficiary_ids=request.filter_by_beneficiary_ids,
            filter_by_created_dates=request.filter_by_created_dates,
        )
        transactions.limit(
            request.page_size or self._default_page_size,
        )

        return grpc_pb2.ListTransactionsResponse(
            transactions=[transaction async for transaction in transactions],
            next_page_token=await transactions.cursor(),
        )

    async def GetTransaction(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetTransactionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetTransactionResponse:
        transaction = await self._transactions.find_by_selector(
            selection_value=request.id,
            selector=request.selector or "_id",
        )

        if transaction is None:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetTransactionResponse(transaction=transaction)

    async def GetTransactions(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetTransactionsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetTransactionsResponse:
        transactions = await self._transactions.find_by_ids(
            list(request.ids),
            request.selector or "_id",
        )

        return grpc_pb2.GetTransactionsResponse(
            transactions=[transaction async for transaction in transactions],
        )

    async def CreateTransaction(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: grpc_pb2.CreateTransactionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateTransactionResponse:
        quotation = await self._quotations.find_by_id(
            request.quotation_id,
        )

        await self._validate_quotation(
            request.quotation_id,
            quotation,
            context,
        )

        exist_transaction = await self._transactions.exists_by_external_reference(
            request.external_reference,
        )
        if exist_transaction:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="external_reference_id",
                    field_description="Transaction already exists",
                ),
            )

        quotation = cast(models_pb2.Quotation, quotation)

        bill = await self._bills.find_by_order_id(request.order_id)
        if bill:
            bill = self._add_amount_to_bill_amount(
                bill,
                quotation.amounts.total_amount,
            )
            await self._bills.update(bill)
        else:
            bill = await self._bills.insert(
                models_pb2.Bill(
                    id=string.uuid(),
                    order_id=request.order_id,
                    total_amount=quotation.amounts.total_amount,
                ),
            )

        transaction_id = string.uuid()

        payer = await self._companies.get(quotation.payer_id)
        charge_amount = money.total(
            [
                money.from_protobuf(quotation.amounts.base_converted),
                money.from_protobuf(quotation.amounts.tax_converted),
            ],
        )
        try:
            execution_status = await self._execute_payment(
                charge_amount,
                payer.payment_reference,
            )
        except adapter_errors.NotFoundError:
            execution_status = False

        charge_status = (
            models_pb2.TransactionStatus.TRANSACTION_STATUS_SUCCEEDED
            if execution_status
            else models_pb2.TransactionStatus.TRANSACTION_STATUS_FAILED
        )
        transaction = models_pb2.Transaction(
            id=transaction_id,
            external_reference_id=request.external_reference,
            invoice_reference_id=request.invoice_reference,
            amounts=quotation.amounts,
            rates=quotation.rates,
            payer_id=quotation.payer_id,
            beneficiary_id=quotation.beneficiary_id,
            payment_type=payer.payment_type,
            payment_method=payer.payment_method,
            bill_id=bill.id,
            status=models_pb2.TransactionStatus.TRANSACTION_STATUS_PENDING,
            charge_status=charge_status,
        )

        inserted_transaction = await self._transactions.insert(
            transaction,
        )

        await self._quotations.update_status(
            request.quotation_id,
            models_pb2.QuotationStatus.QUOTATION_STATUS_CONFIRMED,
        )

        return grpc_pb2.CreateTransactionResponse(transaction=inserted_transaction)

    async def UpdateTransactionStatus(  # type: ignore[override]  # noqa: N802
        self,
        request: grpc_pb2.UpdateTransactionStatusRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateTransactionStatusResponse:
        return grpc_pb2.UpdateTransactionStatusResponse(
            is_success=await self._transactions.update_status(
                request.id,
                request.status,
            ),
        )

    async def UpdateTransactionStatuses(  # type: ignore[override]  # noqa: N802
        self,
        request: grpc_pb2.UpdateTransactionStatusesRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateTransactionStatusesResponse:
        is_success = await self._invoices.update_status(
            request.external_reference_id,
            request.status,
        )
        if not is_success:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        invoice = await self._invoices.find_by_external_id(
            request.external_reference_id,
        )

        is_success = await self._transactions.update_statuses(
            list(invoice.transaction_ids),  # type: ignore[union-attr]
            _TRANSACTION_STATUS_MAPPING[request.status],
        )

        return grpc_pb2.UpdateTransactionStatusesResponse(is_success=is_success)

    def _add_amount_to_bill_amount(
        self,
        bill: models_pb2.Bill,
        amount: money_pb2.Money,
    ) -> models_pb2.Bill:
        added_amount = money.from_protobuf(amount)

        if bill.HasField("total_amount"):
            bill_total_amount = money.from_protobuf(bill.total_amount)
            bill.total_amount.MergeFrom(bill_total_amount.add(added_amount).protobuf())
        else:
            bill.total_amount.MergeFrom(added_amount.protobuf())

        return bill

    async def _execute_payment(
        self,
        amount: money.Money,
        payment_reference: str,
    ) -> bool:
        if not payment_reference:
            return False

        payment_intent = await self._credit_card_client.create_credit_card_payment(
            amount=amount,
            credit_card_holder_id=payment_reference,
            enable_automatic_payment_method=True,
            capture_method="automatic",
            allow_redirect="never",
        )

        processed_payment = await self._credit_card_client.process_credit_card_payment(
            payment_intent.id,
        )

        return processed_payment.status == "succeeded"

    async def _validate_quotation(
        self,
        quotation_id: str,
        quotation: models_pb2.Quotation | None,
        context: grpc.aio.ServicerContext,
    ) -> None:
        if not quotation:
            return await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details="Quotation not found",
                trailing_metadata=(
                    ("field_name", "quotation_id"),
                    (
                        "field_description",
                        "Quotation not found {0}".format(
                            quotation_id,
                        ),
                    ),
                ),
            )

        if quotation.status != models_pb2.QuotationStatus.QUOTATION_STATUS_QUOTED:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="quotation_id",
                    field_description="Quotation not valid",
                ),
            )
        return None


class QuotationsService(
    service.Service,
    grpc_pb2_grpc.QuotationsServiceServicer,
):
    def __init__(
        self,
        quotations: QuotationsRepository,
        user_sessions: UserSessionRepository,
        currencies_client: currencies.Client,
        companies_client: companies.Client,
    ):
        self._quotations = quotations
        self._user_sessions = user_sessions
        self._currencies_client = currencies_client
        self._companies_client = companies_client

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["QuotationsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_QuotationsServiceServicer_to_server(
            self,
            server,
        )

    async def CreateQuotation(  # type: ignore[override]  # noqa: N802, WPS217
        self,
        request: grpc_pb2.CreateQuotationRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateQuotationResponse:
        await self._validate_currencies(
            request.from_currency,
            request.to_currency,
            context,
        )

        try:
            payer = await self._companies_client.get(request.payer_id)
        except adapter_errors.NotFoundError:
            return await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details="Company not found",
                trailing_metadata=(
                    ("field_name", "payer_id"),
                    (
                        "field_description",
                        "Company not found {0}".format(request.payer_id),
                    ),
                ),
            )

        try:
            rate = await self._get_rate(
                request.from_currency,
                request.to_currency,
                request.amount,
                request.session_token,
            )
        except adapter_errors.NotFoundError:
            return await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                details="Currencies pair not supported",
            )

        quote = Quote(
            request.amount,
            money.Currency(request.from_currency),
            money.Currency(request.to_currency),
            rate,
            payer,
            request.beneficiary_id,
            request.tax,
            request.fee_multiplier,
            request.vertical_type,
        )

        quotation = await self._quotations.insert(quote.to_proto())
        return grpc_pb2.CreateQuotationResponse(quotation=quotation)

    async def GetQuotation(  # type: ignore[override]  # noqa: N802
        self,
        request: grpc_pb2.GetQuotationRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetQuotationResponse:
        quotation = await self._quotations.find_by_id(request.id)

        if not quotation:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetQuotationResponse(quotation=quotation)

    async def UpdateQuotationStatus(  # type: ignore[override]  # noqa: N802
        self,
        request: grpc_pb2.UpdateQuotationStatusRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateQuotationStatusResponse:
        return grpc_pb2.UpdateQuotationStatusResponse(
            is_success=await self._quotations.update_status(
                request.id,
                request.status,
            ),
        )

    async def _get_rate(
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
        session_token: str | None,
    ) -> float:
        if from_currency == to_currency:
            return 1.0

        if session_token:
            currency_pair = "{0}{1}".format(from_currency, to_currency)
            cache_key = "locks:{0}:{1}".format(session_token, currency_pair)
            rate = await self._user_sessions.get_rate(session_token, currency_pair)
            if not rate:
                async with self._user_sessions.lock(cache_key):
                    rate = await self._handle_lock(
                        session_token,
                        currency_pair,
                        from_currency,
                        to_currency,
                        amount,
                    )

        else:
            rate = await self._get_live_rate(
                from_currency,
                to_currency,
                amount,
            )

        return rate

    async def _handle_lock(
        self,
        session_token: str,
        currency_pair: str,
        from_currency: str,
        to_currency: str,
        amount: int,
    ) -> float:
        rate = await self._get_live_rate(
            from_currency,
            to_currency,
            amount,
        )
        await self._user_sessions.store(
            session_token,
            currency_pair,
            rate,
        )

        return rate

    async def _get_live_rate(
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
    ) -> float:
        response = await self._currencies_client.convert(
            from_currency=money.Currency(from_currency),
            to_currency=money.Currency(to_currency),
            amount=amount,
        )
        return round(response.rate, 2)

    async def _validate_currencies(
        self,
        from_currency: str,
        to_currency: str,
        context: grpc.aio.ServicerContext,
    ) -> None:
        check_from_currency = self._is_valid_currency(from_currency)
        check_to_currency = self._is_valid_currency(to_currency)
        if not check_from_currency:
            return await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details="Currency not found",
                trailing_metadata=(
                    ("field_name", "from_currency"),
                    (
                        "field_description",
                        "Currency not found {0}".format(from_currency),
                    ),
                ),
            )
        if not check_to_currency:
            return await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details="Currency not found",
                trailing_metadata=(
                    ("field_name", "to_currency"),
                    ("field_description", "Currency not found {0}".format(to_currency)),
                ),
            )
        return None

    def _is_valid_currency(self, currency: str) -> bool:
        try:
            money.Currency(currency)
        except ValueError:
            return False
        return True


class BillsService(
    service.Service,
    grpc_pb2_grpc.BillsServiceServicer,
):
    def __init__(
        self,
        bills: BillsRepository,
    ):
        self._bills = bills
        self._default_page_size = 20
        self._sort = {"updated_at": "updated_at"}

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["BillsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_BillsServiceServicer_to_server(
            self,
            server,
        )

    async def ListBills(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListBillsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListBillsResponse:
        bills = await self._bills.find(
            cursor=request.page_token,
            sort=sorting.get_sort(request.sort_by, self._sort),
            filter_by_order_ids=request.filter_by_order_ids,
        )
        bills.limit(
            request.page_size or self._default_page_size,
        )

        return grpc_pb2.ListBillsResponse(
            bills=[bill async for bill in bills],
            next_page_token=await bills.cursor(),
        )

    async def GetBill(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetBillRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetBillResponse:
        bill = await self._bills.find_by_selector(
            selection_value=request.id,
            selector=request.selector or "_id",
        )

        if bill is None:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetBillResponse(bill=bill)

    async def CreateBill(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateBillRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateBillResponse:
        request.bill.id = string.uuid()

        inserted_bill = await self._bills.insert(request.bill)

        return grpc_pb2.CreateBillResponse(bill=inserted_bill)

    async def UpdateBillReconciliation(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateBillReconciliationRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateBillReconciliationResponse:
        bill = await self._get_bill(context, request.id)

        if request.is_reconciled:
            bill.is_reconciled = request.is_reconciled
            if bill.HasField("total_amount"):
                bill.MergeFrom(
                    models_pb2.Bill(
                        reconciled_amount=bill.total_amount,
                    ),
                )
        else:
            bill.ClearField("reconciled_amount")
            bill.is_reconciled = request.is_reconciled

        return grpc_pb2.UpdateBillReconciliationResponse(
            bill=await self._bills.update(bill),
        )

    async def UpdateBillPaymentIntent(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateBillPaymentIntentRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateBillPaymentIntentResponse:
        bill = await self._get_bill(context, request.id)

        bill.payment_intent_id = request.payment_intent_id

        return grpc_pb2.UpdateBillPaymentIntentResponse(
            bill=await self._bills.update(bill),
        )

    async def _get_bill(
        self,
        context: grpc.aio.ServicerContext,
        identifier: str,
    ) -> models_pb2.Bill:
        bill = await self._bills.find_by_id(identifier)

        if bill is None:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return bill
