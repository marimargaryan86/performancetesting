import grpc

from snowfall.project.pay.service.rates import cache, rates
from snowfall.project.pay.service.rates.v1alpha import (
    models_pb2,
    rates_pb2,
    rates_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class RatesService(service.Service, rates_pb2_grpc.RatesServiceServicer):
    def __init__(
        self,
        backup_rates: rates.BackUpRatesRepository,
        redis_client: cache.RateRepository,
    ):
        self._redis_client = redis_client
        self._backup_rates = backup_rates

    def get_name(self) -> str:
        return rates_pb2.DESCRIPTOR.services_by_name["RatesService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        rates_pb2_grpc.add_RatesServiceServicer_to_server(self, server)

    async def Get(  # type: ignore[override] # noqa: N802
        self,
        request: rates_pb2.GetRequest,
        context: grpc.aio.ServicerContext,
    ) -> rates_pb2.GetResponse:
        rate = await self._redis_client.get(
            "{0}{1}".format(request.sell_currency, request.buy_currency),
        )

        if not rate:
            backup_rate = await self._backup_rates.find_by_currency_pair(
                request.sell_currency,
                request.buy_currency,
            )

            if not backup_rate:
                return await context.abort(grpc.StatusCode.NOT_FOUND)

            rate = backup_rate.rate

        return rates_pb2.GetResponse(
            rate=models_pb2.Rate(
                sell_currency=request.sell_currency,
                buy_currency=request.buy_currency,
                rate=rate,
            ),
        )
