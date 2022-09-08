import grpc

from snowfall.project.pay.service.rates import rates
from snowfall.project.pay.service.rates.v1alpha import rates_pb2, rates_pb2_grpc
from snowfall.stdlib.transport.grpc import service


class RatesService(service.Service, rates_pb2_grpc.RatesServiceServicer):
    def __init__(
        self,
        rates_repository: rates.RatesRepository,
        monitored_rates: rates.MonitoredRatesRepository,
    ):
        self._rates = rates_repository
        self._monitored_rates = monitored_rates

    def get_name(self) -> str:
        return rates_pb2.DESCRIPTOR.services_by_name["RatesService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        rates_pb2_grpc.add_RatesServiceServicer_to_server(self, server)

    async def Insert(  # type: ignore[override] # noqa: N802
        self,
        request: rates_pb2.InsertRequest,
        context: grpc.aio.ServicerContext,
    ) -> rates_pb2.InsertResponse:
        inserted_rates = await self._rates.insert_many(
            request.rates,
        )

        return rates_pb2.InsertResponse(rates=inserted_rates)

    async def Monitor(  # type: ignore[override] # noqa: N802
        self,
        request: rates_pb2.MonitorRequest,
        context: grpc.aio.ServicerContext,
    ) -> rates_pb2.MonitorResponse:
        monitored_rate = await self._monitored_rates.insert(
            request.monitored_rate,
        )

        return rates_pb2.MonitorResponse(monitored_rate=monitored_rate)
