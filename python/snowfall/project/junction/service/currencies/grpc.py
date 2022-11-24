import grpc
import httpx

from snowfall.project.junction.service.currencies.v1alpha import (
    currencies_pb2,
    currencies_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service
from snowfall.vendor.apilayer.client import APILayer
from snowfall.vendor.apilayer.models.exchange import Quote as APILayerQuote
from snowfall.vendor.bound.client import Bound
from snowfall.vendor.bound.models.exchange import Quote as BoundQuote


class CurrencyService(service.Service, currencies_pb2_grpc.CurrencyServiceServicer):
    def __init__(self, api_layer_client: APILayer, bound_client: Bound):
        self.api_layer_client = api_layer_client
        self.bound_client = bound_client

    def get_name(self) -> str:
        return currencies_pb2.DESCRIPTOR.services_by_name["CurrencyService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        currencies_pb2_grpc.add_CurrencyServiceServicer_to_server(self, server)

    async def Convert(  # type: ignore[override] # noqa: N802
        self,
        request: currencies_pb2.ConvertRequest,
        context: grpc.aio.ServicerContext,
    ) -> currencies_pb2.ConvertResponse:
        quote_params = (
            request.from_currency,
            request.to_currency,
            request.amount,
        )

        try:
            quote: BoundQuote | APILayerQuote = await self.api_layer_client.quote(
                *quote_params,
            )
        except httpx.HTTPError:
            quote = await self.bound_client.quote(
                *quote_params,
            )

        return currencies_pb2.ConvertResponse(
            amount=quote.amount,
            rate=quote.rate,
        )
