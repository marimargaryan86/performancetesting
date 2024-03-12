import grpc
from pymongo.errors import DuplicateKeyError

from snowfall.project.pay.service.companies import repositories
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
)
from snowfall.stdlib import string
from snowfall.stdlib.transport.grpc import rich_status, service


class CompaniesService(
    service.Service,
    grpc_pb2_grpc.CompaniesServiceServicer,
):
    def __init__(
        self,
        companies: repositories.CompaniesRepository,
    ):
        self._companies = companies
        self._default_page_size = 20

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["CompaniesService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_CompaniesServiceServicer_to_server(
            self,
            server,
        )

    async def CreateCompany(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateCompanyRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateCompanyResponse:
        request.company.id = string.uuid()

        try:
            inserted_company = await self._companies.insert(request.company)
        except DuplicateKeyError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="name",
                    field_description="name already exists",
                ),
            )

        return grpc_pb2.CreateCompanyResponse(company=inserted_company)

    async def GetCompany(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetCompanyRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetCompanyResponse:
        company = await self._companies.find_by_id(request.id)

        if not company:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetCompanyResponse(company=company)

    async def UpdateCompany(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateCompanyRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateCompanyResponse:
        company = await self._companies.find_by_id(request.company.id)

        if not company:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        if (  # noqa: WPS337
            request.company.address.address_lines and company.address.address_lines
        ):
            company.address.ClearField("address_lines")

        if request.company.fee_amounts:
            company.ClearField("fee_amounts")

        company.MergeFrom(request.company)

        try:
            await self._companies.update(company)
        except DuplicateKeyError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="name",
                    field_description="name already exists",
                ),
            )

        return grpc_pb2.UpdateCompanyResponse(company=company)

    async def ListCompanies(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListCompaniesRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListCompaniesResponse:
        if request.is_accountless:
            companies = await self._companies.find_accountless(
                cursor=request.page_token,
            )
        else:
            companies = await self._companies.find_all(
                identifiers=list(request.ids.ids),
                cursor=request.page_token,
            )

        companies.limit(
            request.page_size or self._default_page_size,
        )

        return grpc_pb2.ListCompaniesResponse(
            companies=[company async for company in companies],
            next_page_token=await companies.cursor(),
        )
