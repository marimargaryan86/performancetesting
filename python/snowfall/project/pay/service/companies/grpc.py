import datetime
from typing import cast

import grpc
from pymongo.errors import DuplicateKeyError

from snowfall.project.pay.service.companies import repositories
from snowfall.project.pay.service.companies.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.grpc import rich_status, service
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models import account as cc_account_models


class CompaniesService(  # noqa: WPS214
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
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetCompanyResponse(company=company)

    async def UpdateCompany(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateCompanyRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateCompanyResponse:
        company = await self._companies.find_by_id(request.company.id)

        if not company:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        if (  # noqa: WPS337
            request.company.address.address_lines
            and company.address.address_lines  # type: ignore[union-attr]
        ):
            company.address.ClearField("address_lines")  # type: ignore[union-attr]

        company.MergeFrom(request.company)  # type: ignore[union-attr]

        try:
            await self._companies.update(company)  # type: ignore[arg-type]
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
                cursor=request.page_token,
            )

        companies.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return grpc_pb2.ListCompaniesResponse(
            companies=[company async for company in companies],
            next_page_token=await companies.cursor(),
        )


class AccountsService(service.Service, grpc_pb2_grpc.AccountsServiceServicer):
    def __init__(
        self,
        accounts: repositories.AccountsRepository,
        payment_client: PaymentClient,
    ):
        self._accounts = accounts
        self._default_page_size = 20
        self._payment_client = payment_client

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["AccountsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_AccountsServiceServicer_to_server(self, server)

    async def CreateAccount(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateAccountRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateAccountResponse:
        request.account.id = string.uuid()
        inserted_account = await self._accounts.insert(request.account)

        return grpc_pb2.CreateAccountResponse(account=inserted_account)

    async def GetAccount(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetAccountRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetAccountResponse:
        account = await self._accounts.find_by_id(request.id)

        if not account:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetAccountResponse(account=account)

    async def ListAccounts(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListAccountsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListAccountsResponse:
        db_accounts = await self._accounts.find(
            cursor=request.page_token,
            limit=request.page_size or self._default_page_size,
            filter_by=request.filter_by,
        )
        return grpc_pb2.ListAccountsResponse(
            accounts=[account async for account in db_accounts],
            next_page_token=await db_accounts.cursor(),
        )

    async def UpdateAccountStatus(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateAccountStatusRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateAccountStatusResponse:
        account = await self._accounts.find_by_id(request.id)
        if account is None:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        account = cast(models_pb2.Account, account)
        await self._payment_client.update_account(
            account.external_reference,
            cc_account_models.AccountUpdateRequest(
                status=cc_account_models.StatusEnum(
                    protobuf.enum_value_to_slug(
                        models_pb2.Status.DESCRIPTOR,
                        request.status,
                    ).replace("-", "_"),
                ),
            ),
        )
        update_result = await self._accounts.update(
            request.id,
            {
                "status": request.status,
                "updated_at": datetime.datetime.now(tz=datetime.UTC),
            },
        )
        if update_result.matched_count == 0:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        account.status = request.status

        return grpc_pb2.UpdateAccountStatusResponse(
            account=account,
        )


class ContactsService(service.Service, grpc_pb2_grpc.ContactsServiceServicer):
    def __init__(self, contacts: repositories.ContactsRepository):
        self._contacts = contacts
        self._default_page_size = 20

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["ContactsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_ContactsServiceServicer_to_server(self, server)

    async def CreateContact(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateContactRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateContactResponse:
        request.contact.id = string.uuid()
        inserted_contact = await self._contacts.insert(request.contact)

        return grpc_pb2.CreateContactResponse(contact=inserted_contact)

    async def GetContact(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetContactRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetContactResponse:
        contact = await self._contacts.find_by_id(request.id)

        if not contact:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetContactResponse(contact=contact)
