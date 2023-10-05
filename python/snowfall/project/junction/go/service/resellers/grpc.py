import json
from collections.abc import Sequence

from grpc import StatusCode, aio

from snowfall.project.junction.go.service.resellers import resellers_repository
from snowfall.project.junction.go.service.resellers.v1 import (
    models_pb2,
    resellers_pb2,
    resellers_pb2_grpc,
)
from snowfall.stdlib import string
from snowfall.stdlib.transport.grpc import service
from snowfall.vendor.consul.client import ConsulClient

_PROVIDERS_KEY = "{0}/providers/reseller-providers"
_CURRENCIES_KEY = "{0}/client-api/reseller-currencies"


class ResellerService(  # noqa: WPS214
    service.Service,
    resellers_pb2_grpc.ResellerServiceServicer,
):
    def __init__(
        self,
        default_page_size: int,
        resellers_repo: resellers_repository.ResellerRepository,
        consul_client: ConsulClient,
        environment: str,
    ):
        self._default_page_size = default_page_size
        self._repository = resellers_repo
        self._client = consul_client
        self._reseller_providers_key = _PROVIDERS_KEY.format(environment)
        self._reseller_currencies_key = _CURRENCIES_KEY.format(environment)

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
        if not await self._repository.exists(request.reseller.id):
            await context.abort(StatusCode.NOT_FOUND)

        await self._repository.upsert(request.reseller)

        return resellers_pb2.UpdateResellerResponse(reseller=request.reseller)

    async def PromoteResellerConfig(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.PromoteResellerConfigRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.PromoteResellerConfigResponse:
        resellers = [reseller async for reseller in await self._repository.all_()]

        reseller_config_updated = await self._update_resellers_config(resellers)
        currencies_config_updated = await self._update_currencies_config(resellers)

        if not currencies_config_updated or not reseller_config_updated:
            await context.abort(StatusCode.FAILED_PRECONDITION)

        return resellers_pb2.PromoteResellerConfigResponse()

    async def _update_resellers_config(
        self,
        resellers: Sequence[models_pb2.Reseller],
    ) -> bool:
        reseller_providers_mapping = json.loads(
            await self._client.get_key(self._reseller_providers_key),
        )

        for reseller in resellers:
            reseller_providers_mapping[reseller.id] = list(reseller.provider_ids)

        return await self._client.put_key(
            self._reseller_providers_key,
            json.dumps(reseller_providers_mapping).encode(),
        )

    async def _update_currencies_config(
        self,
        resellers: Sequence[models_pb2.Reseller],
    ) -> bool:
        reseller_currencies_mapping = json.loads(
            await self._client.get_key(self._reseller_currencies_key),
        )

        for reseller in resellers:
            reseller_currencies_mapping[reseller.id] = reseller.default_currency

        return await self._client.put_key(
            self._reseller_currencies_key,
            json.dumps(reseller_currencies_mapping).encode(),
        )
