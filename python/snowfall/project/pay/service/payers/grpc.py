import grpc

from snowfall.project.pay.service.payers import payers
from snowfall.project.pay.service.payers.v1alpha import payers_pb2, payers_pb2_grpc
from snowfall.stdlib.transport.grpc import service


class PayerService(service.Service, payers_pb2_grpc.PayersServiceServicer):
    def __init__(
        self,
        payers_repository: payers.PayersRepository,
        default_page_size: int,
    ):
        self._payers = payers_repository
        self._default_page_size = default_page_size

    def get_name(self) -> str:
        return payers_pb2.DESCRIPTOR.services_by_name["PayersService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        payers_pb2_grpc.add_PayersServiceServicer_to_server(self, server)

    async def CreatePayer(  # type: ignore[override] # noqa: N802
        self,
        request: payers_pb2.CreatePayerRequest,
        context: grpc.aio.ServicerContext,
    ) -> payers_pb2.CreatePayerResponse:
        payer = await self._payers.insert(
            request.payer,
        )

        return payers_pb2.CreatePayerResponse(payer=payer)

    async def GetPayer(  # type: ignore[override] # noqa: N802
        self,
        request: payers_pb2.GetPayerRequest,
        context: grpc.aio.ServicerContext,
    ) -> payers_pb2.GetPayerResponse:
        payer = await self._payers.find_by_id(request.id)

        return payers_pb2.GetPayerResponse(payer=payer)

    async def ListPayers(  # type: ignore[override] # noqa: N802
        self,
        request: payers_pb2.ListPayersRequest,
        context: grpc.ServicerContext,
    ) -> payers_pb2.ListPayersResponse:
        payers_result = await self._payers.find(request.page_token)

        payers_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return payers_pb2.ListPayersResponse(
            payers=[payer async for payer in payers_result],
            next_page_token=await payers_result.cursor(),
        )
