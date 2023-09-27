import uuid

from grpc import StatusCode, aio

from snowfall.project.junction.go.service.resellers import resellers_repository
from snowfall.project.junction.go.service.resellers.v1 import (
    models_pb2,
    resellers_pb2,
    resellers_pb2_grpc,
)
from snowfall.stdlib import string
from snowfall.stdlib.transport.grpc import service


class ResellerService(  # noqa: WPS214
    service.Service,
    resellers_pb2_grpc.ResellerServiceServicer,
):
    def __init__(
        self,
        default_page_size: int,
        resellers_repo: resellers_repository.ResellerRepository,
    ):
        self._default_page_size = default_page_size
        self._repository = resellers_repo

    def get_name(self) -> str:
        return models_pb2.DESCRIPTOR.services_by_name["ResellerService"].full_name

    def register(self, server: aio.Server) -> None:
        resellers_pb2_grpc.add_ResellerServiceServicer_to_server(self, server)

    async def CreateReseller(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.CreateResellerRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.CreateResellerResponse:
        request.reseller.id = string.uuid()

        return resellers_pb2.CreateResellerResponse(
            reseller=await self._repository.insert(
                request.reseller,
            ),
        )

    async def GetReseller(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.GetResellerRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.GetResellerResponse:
        reseller = await self._repository.find_by_id(request.id)
        if not reseller:
            await context.abort(StatusCode.NOT_FOUND)

        return resellers_pb2.GetResellerResponse(
            reseller=reseller,
        )

    async def ListResellers(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.ListResellersRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.ListResellersResponse:
        resellers_res = await self._repository.find(cursor=request.page_token)

        resellers_res.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        resellers = [reseller async for reseller in resellers_res]

        return resellers_pb2.ListResellersResponse(
            resellers=resellers,
            next_page_token=await resellers_res.cursor(),
        )

    async def UpdateReseller(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.UpdateResellerRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.UpdateResellerResponse:
        reseller = await self._repository.find_by_id(request.id)

        if not reseller:
            await context.abort(StatusCode.NOT_FOUND)

        if request.providers:
            reseller.ClearField("providers")  # type: ignore[union-attr]

        reseller.MergeFrom(  # type: ignore[union-attr]
            models_pb2.Reseller(
                name=request.name,
                default_currency=request.default_currency,
                providers=request.providers,
            ),
        )

        await self._repository.update(reseller)  # type: ignore[arg-type]

        return resellers_pb2.UpdateResellerResponse(reseller=reseller)

    async def DeleteReseller(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.DeleteResellerRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.DeleteResellerResponse:
        try:
            uuid.UUID(request.id)
        except ValueError:
            await context.abort(StatusCode.INVALID_ARGUMENT)

        await self._repository.delete(request.id)

        return resellers_pb2.DeleteResellerResponse()
