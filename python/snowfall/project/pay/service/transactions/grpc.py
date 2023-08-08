import grpc

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.adapter import errors as adapter_errors
from snowfall.project.pay.adapter import companies, currencies, lead_companies
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import PaymentType
from snowfall.project.pay.service.transactions.cache import UserSessionRepository
from snowfall.project.pay.service.transactions.quote import Quote
from snowfall.project.pay.service.transactions.transactions import (
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
from snowfall.stdlib.transport.grpc import service
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models import conversion


class TransactionsService(
    service.Service,
    grpc_pb2_grpc.TransactionsServiceServicer,
):
    def __init__(
        self,
        transactions: TransactionsRepository,
        conversions: ConversionsRepository,
        payment_client: PaymentClient,
        companies_client: companies.Client,
    ):
        self._transactions = transactions
        self._conversions = conversions
        self._payment_client = payment_client
        self._companies = companies_client
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
        transaction = await self._transactions.find_by_id(
            request.id,
            request.selector if request.selector else "_id",
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

    async def CreateTransaction(  # type: ignore[override] # noqa: N802, WPS210
        self,
        request: grpc_pb2.CreateTransactionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateTransactionResponse:
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
            ),
        )

        return grpc_pb2.CreateTransactionResponse(transaction=inserted_transaction)


class QuotationsService(  # noqa: WPS214
    service.Service,
    grpc_pb2_grpc.QuotationsServiceServicer,
):
    def __init__(
        self,
        quotations: QuotationsRepository,
        user_sessions: UserSessionRepository,
        currencies_client: currencies.Client,
        lead_company_client: lead_companies.Client,
    ):
        self._quotations = quotations
        self._user_sessions = user_sessions
        self._currencies_client = currencies_client
        self._lead_companies_client = lead_company_client

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

        try:
            lead_company = await self._lead_companies_client.get(
                request.payer.lead_company_id,
            )
        except errors.NotFoundError:
            lead_company = None

        quote = Quote(
            request.amount,
            money.Currency(request.from_currency),
            money.Currency(request.to_currency),
            rate,
            request.payer,
            lead_company,
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
            async with self._user_sessions.lock(cache_key):
                rate = await self._user_sessions.get_rate(session_token, currency_pair)

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
        else:
            rate = await self._get_live_rate(
                from_currency,
                to_currency,
                amount,
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
