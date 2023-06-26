from decimal import Decimal

import grpc

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.adapter import rates
from snowfall.project.pay.service.currencies.repositories import CurrencyRepository
from snowfall.project.pay.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.money import Currency, Money
from snowfall.stdlib.transport.grpc import service

_DEFAULT_PAGE_SIZE = 20


class CurrencyService(service.Service, currencies_pb2_grpc.CurrencyServiceServicer):
    def __init__(
        self,
        rates_service: rates.GrpcClient,
        currencies: CurrencyRepository,
    ):
        self._rates_service = rates_service
        self._currencies = currencies

    def get_name(self) -> str:
        return currencies_pb2.DESCRIPTOR.services_by_name["CurrencyService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        currencies_pb2_grpc.add_CurrencyServiceServicer_to_server(self, server)

    async def Convert(  # type: ignore[override] # noqa: N802
        self,
        request: currencies_pb2.ConvertRequest,
        context: grpc.aio.ServicerContext,
    ) -> currencies_pb2.ConvertResponse:
        try:
            quote = await self._rates_service.get_rate(
                Currency(request.from_currency),
                Currency(request.to_currency),
            )
        except errors.NotFoundError:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        base_amount = Money(request.amount, Currency(request.from_currency))
        conversion = base_amount.convert(
            Currency(request.to_currency),
            Decimal(quote.rate),
        )

        return currencies_pb2.ConvertResponse(
            amount=conversion.amount,
            rate=quote.rate,
        )

    async def Get(  # type: ignore[override] # noqa: N802
        self,
        request: currencies_pb2.GetRequest,
        context: grpc.aio.ServicerContext,
    ) -> currencies_pb2.GetResponse:
        currency = self._currencies.find_by_id(request.currency)
        if not currency:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                details="{0} currency not supported".format(request.currency),
            )
        return currencies_pb2.GetResponse(
            currency=models_pb2.Currency(
                code=currency.code,  # type: ignore[union-attr]
                name=currency.currency_name,  # type: ignore[union-attr]
                exponent=currency.exponent or 0,  # type: ignore[union-attr]
            ),
        )

    async def Find(  # type: ignore[override] # noqa: N802
        self,
        request: currencies_pb2.FindRequest,
        context: grpc.aio.ServicerContext,
    ) -> currencies_pb2.FindResponse:
        page = sequence.paginate(
            sequence=self._currencies.find(),
            cursor=request.page_token,
            limit=request.page_size or _DEFAULT_PAGE_SIZE,
        )
        return currencies_pb2.FindResponse(
            currencies=[
                models_pb2.Currency(
                    code=currency.code,
                    name=currency.currency_name,
                    exponent=currency.exponent or 0,
                )
                for currency in page.sequence
            ],
            next_page_token=page.cursor,
        )
