from decimal import Decimal

import grpc

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.adapter import rates
from snowfall.project.pay.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
)
from snowfall.stdlib.money import Currency, Money
from snowfall.stdlib.transport.grpc import service


class CurrencyService(service.Service, currencies_pb2_grpc.CurrencyServiceServicer):
    def __init__(
        self,
        rates_service: rates.GrpcClient,
    ):
        self._rates_service = rates_service

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
