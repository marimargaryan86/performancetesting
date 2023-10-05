import grpc

from snowfall.project.junction.go.adapter import errors as adapter_errors
from snowfall.project.pay.adapter import companies, currencies
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import PaymentType
from snowfall.project.pay.service.transactions.cache import UserSessionRepository
from snowfall.project.pay.service.transactions.quote import Quote
from snowfall.project.pay.service.transactions.transactions import (
    BillsRepository,
    ConversionsRepository,
    QuotationsRepository,
    TransactionsRepository,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.transport.grpc import service, sorting
from snowfall.stdlib.v1 import money_pb2
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models import conversion


class TransactionsService(  # noqa:WPS214
    service.Service,
    grpc_pb2_grpc.TransactionsServiceServicer,
):
    def __init__(  # noqa: WPS211
        self,
        transactions: TransactionsRepository,
        conversions: ConversionsRepository,
        bills: BillsRepository,
        payment_client: PaymentClient,
        companies_client: companies.Client,
    ):
        self._transactions = transactions
        self._conversions = conversions
        self._bills = bills
        self._payment_client = payment_client
        self._companies = companies_client
        self._sort = {"created_at": "created_at"}
        self._default_page_size = 20

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
        )
        transactions.limit(
            request.page_size if request.page_size else self._default_page_size,
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
            selector=request.selector if request.selector else "_id",
        )

        if transaction is None:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetTransactionResponse(transaction=transaction)

    async def GetTransactions(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetTransactionsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetTransactionsResponse:
        transactions = await self._transactions.find_by_ids(
            list(request.ids),
            request.selector if request.selector else "_id",
        )

        return grpc_pb2.GetTransactionsResponse(
            transactions=[transaction async for transaction in transactions],
        )

    async def CreateTransaction(  # type: ignore[override] # noqa: N802, WPS210, WPS217
        self,
        request: grpc_pb2.CreateTransactionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateTransactionResponse:
        bill = await self._bills.find_by_order_id(request.order_id)
        if bill:
            bill = self._add_amount_to_bill_amount(
                bill,
                request.quotation.amounts.total_amount,
            )
            await self._bills.update(bill)
        else:
            bill = await self._bills.insert(
                models_pb2.Bill(
                    id=string.uuid(),
                    order_id=request.order_id,
                    total_amount=request.quotation.amounts.total_amount,
                ),
            )

        transaction_id = string.uuid()
        are_currencies_same = (
            request.quotation.amounts.base_converted.currency_code
            == request.quotation.amounts.beneficiary.currency_code
        )
        conversion_id = ""
        payer = await self._companies.get(request.quotation.payer_id)
        if (  # noqa: WPS337
            payer.payment_type != PaymentType.PAYMENT_TYPE_CARD
            and not are_currencies_same
        ):
            conversion_response = await _create_conversion(
                grpc_pb2.CreateConversionRequest(
                    beneficiary_amount=request.quotation.amounts.beneficiary,
                    base_converted_amount=request.quotation.amounts.base_converted,
                    transaction_id=transaction_id,
                ),
                self._payment_client,
                self._conversions,
            )
            conversion_id = conversion_response.conversion.id

        inserted_transaction = await self._transactions.insert(
            models_pb2.Transaction(
                id=transaction_id,
                external_reference_id=request.external_reference,
                invoice_reference_id=request.invoice_reference,
                conversion_id=conversion_id,
                amounts=request.quotation.amounts,
                rates=request.quotation.rates,
                payer_id=request.quotation.payer_id,
                beneficiary_id=request.quotation.beneficiary_id,
                payment_type=payer.payment_type,
                payment_method=payer.payment_method,
                bill_id=bill.id,
            ),
        )

        return grpc_pb2.CreateTransactionResponse(transaction=inserted_transaction)

    def _add_amount_to_bill_amount(
        self,
        bill: models_pb2.Bill,
        amount: money_pb2.Money,
    ) -> models_pb2.Bill:
        bill_total_amount = money.from_protobuf(bill.total_amount)
        added_amount = money.from_protobuf(amount)
        bill.total_amount.MergeFrom(bill_total_amount.add(added_amount).protobuf())

        return bill


class QuotationsService(  # noqa: WPS214
    service.Service,
    grpc_pb2_grpc.QuotationsServiceServicer,
):
    def __init__(
        self,
        quotations: QuotationsRepository,
        user_sessions: UserSessionRepository,
        currencies_client: currencies.Client,
    ):
        self._quotations = quotations
        self._user_sessions = user_sessions
        self._currencies_client = currencies_client

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["QuotationsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_QuotationsServiceServicer_to_server(
            self,
            server,
        )

    async def CreateQuotation(  # type: ignore[override]  # noqa: N802
        self,
        request: grpc_pb2.CreateQuotationRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateQuotationResponse:
        # TODO: validation for companies and currency when we create the microservices
        try:
            rate = await self._get_rate(
                request.from_currency,
                request.to_currency,
                request.amount,
                request.session_token,
            )
        except adapter_errors.NotFoundError:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                details="Currencies pair not supported",
            )
            raise RuntimeError() from None  # TODO: Remove when grpcio types are available.

        quote = Quote(
            request.amount,
            money.Currency(request.from_currency),
            money.Currency(request.to_currency),
            rate,
            request.payer,
            request.beneficiary_company.id,
            request.tax,
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
            await context.abort(grpc.StatusCode.NOT_FOUND)

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

    async def _handle_lock(  # noqa: WPS211
        self,
        session_token: str,
        currency_pair: str,
        from_currency: str,
        to_currency: str,
        amount: int,
    ) -> float:
        rate = await self._user_sessions.get_rate(
            session_token,
            currency_pair,
        )
        if not rate:
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
        if from_currency == to_currency:
            rate = 1.0
        else:
            response = await self._currencies_client.convert(
                from_currency=money.Currency(from_currency),
                to_currency=money.Currency(to_currency),
                amount=amount,
            )
            rate = round(response.rate, 2)
        return rate


class ConversionsService(
    service.Service,
    grpc_pb2_grpc.ConversionsServiceServicer,
):
    def __init__(
        self,
        conversions: ConversionsRepository,
    ):
        self._conversions = conversions
        self._default_page_size = 20

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["ConversionsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_ConversionsServiceServicer_to_server(
            self,
            server,
        )

    async def GetConversion(  # type: ignore[override]  # noqa: N802
        self,
        request: grpc_pb2.GetConversionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetConversionResponse:
        conversion_result = await self._conversions.find_by_id(request.id)

        if not conversion_result:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetConversionResponse(conversion=conversion_result)

    async def ListConversions(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListConversionsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListConversionsResponse:
        conversions = await self._conversions.find(
            cursor=request.page_token,
        )
        conversions.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return grpc_pb2.ListConversionsResponse(
            conversions=[conversion_result async for conversion_result in conversions],
            next_page_token=await conversions.cursor(),
        )


class BillsService(  # noqa: WPS214
    service.Service,
    grpc_pb2_grpc.BillsServiceServicer,
):
    def __init__(
        self,
        bills: BillsRepository,
    ):
        self._bills = bills
        self._default_page_size = 20

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
        )
        bills.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return grpc_pb2.ListBillsResponse(
            bills=[bill async for bill in bills],
            next_page_token=await bills.cursor(),
        )

    async def GetBill(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetTransactionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetBillResponse:
        bill = await self._get_bill(context, request.id)

        return grpc_pb2.GetBillResponse(bill=bill)

    async def CreateBill(  # type: ignore[override] # noqa: N802, WPS210
        self,
        request: grpc_pb2.CreateBillRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateBillResponse:
        request.bill.id = string.uuid()

        inserted_bill = await self._bills.insert(request.bill)

        return grpc_pb2.CreateBillResponse(bill=inserted_bill)

    async def UpdateBillReconciliation(  # type: ignore[override] # noqa: N802, WPS210
        self,
        request: grpc_pb2.UpdateBillReconciliationRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateBillReconciliationResponse:
        bill = await self._get_bill(context, request.id)

        if request.is_reconciled:
            bill.MergeFrom(
                models_pb2.Bill(
                    reconciled_amount=bill.total_amount,
                    is_reconciled=request.is_reconciled,
                ),
            )
        else:
            bill.ClearField("reconciled_amount")
            bill.is_reconciled = request.is_reconciled

        return grpc_pb2.UpdateBillReconciliationResponse(
            bill=await self._bills.update(bill),
        )

    async def _get_bill(
        self,
        context: grpc.aio.ServicerContext,
        identifier: str,
    ) -> models_pb2.Bill:
        bill = await self._bills.find_by_id(identifier)

        if bill is None:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return bill  # type: ignore[return-value]


async def _create_conversion(
    request: grpc_pb2.CreateConversionRequest,
    payment_client: PaymentClient,
    conversions: ConversionsRepository,
) -> grpc_pb2.CreateConversionResponse:
    try:
        cc_conversion = await payment_client.create_conversion(
            conversion.ConversionRequest(
                buy_currency=request.beneficiary_amount.currency_code,
                sell_currency=request.base_converted_amount.currency_code,
                amount=str(
                    money.from_protobuf(request.beneficiary_amount),
                ),
                reason=request.transaction_id,
            ),
        )
    except CurrencyCloudError:
        inserted_conversion = await conversions.insert(
            models_pb2.Conversion(
                id=string.uuid(),
                buy_amount=request.beneficiary_amount,
                status=models_pb2.Conversion.Status.STATUS_FAILED,
            ),
        )
    else:
        inserted_conversion = await conversions.create(
            cc_conversion,
        )

    return grpc_pb2.CreateConversionResponse(conversion=inserted_conversion)
