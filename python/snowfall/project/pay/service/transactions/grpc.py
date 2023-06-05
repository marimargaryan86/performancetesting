import grpc

from snowfall.project.junction.go.adapter import errors as adapter_errors
from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.transactions.cache import UserSessionRepository
from snowfall.project.pay.service.transactions.quote import Quote
from snowfall.project.pay.service.transactions.transactions import (
    QuotationsRepository,
    TransactionsRepository,
)
from snowfall.project.pay.service.transactions.v1alpha import grpc_pb2, grpc_pb2_grpc
from snowfall.stdlib.money import Currency
from snowfall.stdlib.transport.grpc import service


class TransactionsService(
    service.Service,
    grpc_pb2_grpc.TransactionsServiceServicer,
):
    def __init__(
        self,
        transactions: TransactionsRepository,
    ):
        self._transactions = transactions
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
        quote = Quote(
            request.amount,
            Currency(request.from_currency),
            Currency(request.to_currency),
            rate,
            request.payer,
            request.beneficiary_company.id,
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
                from_currency=Currency(from_currency),
                to_currency=Currency(to_currency),
                amount=amount,
            )
            rate = round(response.rate, 2)
        return rate
