from decimal import Decimal

import grpc
import httpx

from snowfall.project.junction.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
)
from snowfall.project.pay.service.rates.rates import BackUpRatesRepository
from snowfall.stdlib.money import Currency, Money
from snowfall.stdlib.transport.grpc import service
from snowfall.vendor.apilayer.client import APILayer
from snowfall.vendor.bound.client import Bound


class CurrencyService(service.Service, currencies_pb2_grpc.CurrencyServiceServicer):
    def __init__(
        self,
        api_layer_client: APILayer,
        bound_client: Bound,
        backup_rates: BackUpRatesRepository,
    ):
        self.api_layer_client = api_layer_client
        self.bound_client = bound_client
        self.backup_rates = backup_rates

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
            quote = await self.api_layer_client.quote(
                request.to_currency,
                request.from_currency,
                request.amount,
            )

        except httpx.HTTPError:
            response = await self._get_failover_rates(
                request.from_currency,
                request.to_currency,
                request.amount,
                context,
            )
        else:
            response = currencies_pb2.ConvertResponse(
                amount=quote.amount,
                rate=quote.rate,
            )

        return response

    async def _get_failover_rates(
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
        context: grpc.aio.ServicerContext,
    ) -> currencies_pb2.ConvertResponse:
        try:
            quote = await self.bound_client.quote(to_currency, from_currency, amount)
        except httpx.HTTPError:
            backup_rate = await self.backup_rates.find_by_currency_pair(
                from_currency,
                to_currency,
            )
            if not backup_rate:
                await context.abort(grpc.StatusCode.NOT_FOUND)
                # TODO: Remove after https://github.com/grpc/grpc/pull/31879
                raise RuntimeError() from None

            base_amount = Money(amount, Currency(from_currency))
            conversion = base_amount.convert(
                Currency(to_currency),
                Decimal(backup_rate.rate),
            )
            response = currencies_pb2.ConvertResponse(
                amount=conversion.amount,
                rate=backup_rate.rate,
            )
        else:
            response = currencies_pb2.ConvertResponse(
                amount=quote.amount,
                rate=quote.rate,
            )

        return response
