import grpc

from snowfall.project.junction.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service
from snowfall.vendor.bound.client import Bound


class CurrencyService(service.Service, currencies_pb2_grpc.CurrencyServiceServicer):
    def __init__(self, client: Bound):
        self.client = client

    def get_name(self) -> str:
        return currencies_pb2.DESCRIPTOR.services_by_name["CurrencyService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        currencies_pb2_grpc.add_CurrencyServiceServicer_to_server(self, server)

    async def Convert(  # type: ignore[override] # noqa: N802
        self,
        request: currencies_pb2.ConvertRequest,
        context: grpc.aio.ServicerContext,
    ) -> currencies_pb2.ConvertResponse:
        quote = await self.client.quote(
            request.to_currency,
            request.from_currency,
            request.amount,
        )

        return currencies_pb2.ConvertResponse(
            amount=quote.amount,
            rate=quote.rate,
        )
