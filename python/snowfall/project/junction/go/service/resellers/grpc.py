import asyncio
import json
from collections.abc import Sequence
from contextlib import suppress

from grpc import StatusCode, aio

from snowfall.project.junction.go.adapter.errors import NotFoundError
from snowfall.project.junction.go.service.resellers import persistence
from snowfall.project.junction.go.service.resellers.v1 import (
    models_pb2,
    resellers_pb2,
    resellers_pb2_grpc,
)
from snowfall.project.pay.adapter import companies as companies_adapter
from snowfall.project.pay.adapter import currencies as currencies_adapter
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.grpc import rich_status, service
from snowfall.vendor.consul.client import ConsulClient

_PROVIDERS_KEY = "{0}/providers/reseller-providers"
_CURRENCIES_KEY = "{0}/client-api/reseller-currencies"
_COMPANIES_KEY = "{0}/client-api/reseller-pay-companies"


class ResellerService(
    service.Service,
    resellers_pb2_grpc.ResellerServiceServicer,
):
    def __init__(
        self,
        default_page_size: int,
        resellers_repo: persistence.ResellerRepository,
        consul_client: ConsulClient,
        environment: str,
        company_client: companies_adapter.Client,
        currency_client: currencies_adapter.Client,
    ):
        self._default_page_size = default_page_size
        self._repository = resellers_repo
        self._client = consul_client
        self._reseller_providers_key = _PROVIDERS_KEY.format(environment)
        self._reseller_currencies_key = _CURRENCIES_KEY.format(environment)
        self._reseller_companies_key = _COMPANIES_KEY.format(environment)
        self._company_client = company_client
        self._currency_client = currency_client
        self._promote_task: asyncio.Task[None] | None = None

    def get_name(self) -> str:
        return models_pb2.DESCRIPTOR.services_by_name["ResellerService"].full_name

    def register(self, server: aio.Server) -> None:
        resellers_pb2_grpc.add_ResellerServiceServicer_to_server(self, server)

    async def CreateReseller(  # type: ignore[override] # noqa: N802,WPS217
        self,
        request: resellers_pb2.CreateResellerRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.CreateResellerResponse:
        if self._promote_task:
            self._promote_task.cancel()

        try:
            await self._company_client.get(request.reseller.company_id)
        except NotFoundError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="company",
                    field_description="Company is not found",
                ),
            )

        try:
            await self._currency_client.get(request.reseller.default_currency)
        except NotFoundError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="currency",
                    field_description="Currency is not found",
                ),
            )
        request.reseller.id = string.uuid()

        reseller = await self._repository.insert(request.reseller)

        await self._schedule_promote_reseller_config()

        return resellers_pb2.CreateResellerResponse(reseller=reseller)

    async def GetReseller(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.GetResellerRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.GetResellerResponse:
        reseller = await self._repository.find_by_id(request.id)
        if not reseller:
            return await context.abort(StatusCode.NOT_FOUND)

        return resellers_pb2.GetResellerResponse(
            reseller=reseller,
        )

    async def ListResellers(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.ListResellersRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.ListResellersResponse:
        resellers_res = await self._repository.find(
            identifiers=list(request.ids.ids),
            cursor=request.page_token,
        )

        resellers_res.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        resellers = [reseller async for reseller in resellers_res]

        return resellers_pb2.ListResellersResponse(
            resellers=resellers,
            next_page_token=await resellers_res.cursor(),
        )

    async def UpdateReseller(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: resellers_pb2.UpdateResellerRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.UpdateResellerResponse:
        if self._promote_task:
            self._promote_task.cancel()

        reseller = await self._repository.find_by_id(request.reseller.id)

        if not reseller:
            return await context.abort(StatusCode.NOT_FOUND)

        if request.reseller.company_id:
            try:
                await self._company_client.get(request.reseller.company_id)
            except NotFoundError:
                await rich_status.abort_with_rich_status(
                    context=context,
                    status=rich_status.build_bad_request(
                        field_name="company",
                        field_description="Company is not found",
                    ),
                )

        if request.reseller.default_currency:
            try:
                await self._currency_client.get(request.reseller.default_currency)
            except NotFoundError:
                await rich_status.abort_with_rich_status(
                    context=context,
                    status=rich_status.build_bad_request(
                        field_name="currency",
                        field_description="Currency is not found",
                    ),
                )

        new_reseller = protobuf.apply_field_mask(
            request.update_mask,
            request.reseller,
            reseller,
            replace_repeated_field=True,
        )

        if not request.reseller.default_currency:
            new_reseller.default_currency = reseller.default_currency

        if not request.reseller.company_id:
            new_reseller.company_id = reseller.company_id

        await self._repository.upsert(new_reseller)

        await self._schedule_promote_reseller_config()

        return resellers_pb2.UpdateResellerResponse(reseller=new_reseller)

    async def PromoteResellerConfig(  # type: ignore[override] # noqa: N802
        self,
        request: resellers_pb2.PromoteResellerConfigRequest,
        context: aio.ServicerContext,
    ) -> resellers_pb2.PromoteResellerConfigResponse:
        try:
            await self.promote_reseller_config()
        except ValueError:
            await context.abort(StatusCode.FAILED_PRECONDITION)

        return resellers_pb2.PromoteResellerConfigResponse()

    async def promote_reseller_config(self) -> None:
        resellers = [reseller async for reseller in await self._repository.all_()]

        reseller_config_updated = await self._update_resellers_config(resellers)
        currencies_config_updated = await self._update_currencies_config(resellers)
        companies_config_updated = await self._update_companies_config(resellers)

        if (  # noqa: WPS337
            not currencies_config_updated
            or not reseller_config_updated
            or not companies_config_updated
        ):
            raise ValueError("No config updated")

    async def _schedule_promote_reseller_config(self) -> None:
        """Schedule promotion soon (resetting the timeout if already scheduled)."""
        task = self._promote_task
        # Must not have an await between create_task() and .cancel().
        self._promote_task = asyncio.create_task(self._promote_soon())
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    async def _promote_soon(self) -> None:
        """Delay promotion, so multiple changes can be batched together."""
        await asyncio.sleep(60)
        await self.promote_reseller_config()

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
            json.dumps(reseller_providers_mapping, indent=4, sort_keys=True).encode(),
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
            json.dumps(reseller_currencies_mapping, indent=4, sort_keys=True).encode(),
        )

    async def _update_companies_config(
        self,
        resellers: Sequence[models_pb2.Reseller],
    ) -> bool:
        reseller_companies_mapping = json.loads(
            await self._client.get_key(self._reseller_companies_key),
        )

        for reseller in resellers:
            reseller_companies_mapping[reseller.id] = reseller.company_id

        return await self._client.put_key(
            self._reseller_companies_key,
            json.dumps(reseller_companies_mapping, indent=4, sort_keys=True).encode(),
        )
