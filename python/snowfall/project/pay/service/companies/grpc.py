import datetime

import grpc
from pymongo.errors import DuplicateKeyError

from snowfall.project.pay.adapter import invoice_payment
from snowfall.project.pay.service.companies import repositories
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.grpc import rich_status, service


class CompaniesService(
    service.Service,
    grpc_pb2_grpc.CompaniesServiceServicer,
):
    def __init__(
        self,
        companies: repositories.CompaniesRepository,
        invoice_client: invoice_payment.Client,
    ):
        self._companies = companies
        self._invoice_client = invoice_client
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

        request.company.invoice_generation_date = protobuf.date_to_protobuf(  # type: ignore[misc]
            datetime.datetime.now(tz=datetime.UTC)
            + datetime.timedelta(request.company.invoice_generation_frequency),
        )

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
        inserted_company = await self._create_invoice_account(inserted_company)

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

    async def _create_invoice_account(
        self,
        company: models_pb2.Company,
    ) -> models_pb2.Company:
        if company.create_invoice_account:
            invoice_account = await self._invoice_client.create_account(
                company.finance_email,
                company.name,
            )
            company.payment_reference = invoice_account.id
            company = await self._companies.update(company)

        return company


class ContactsService(service.Service, grpc_pb2_grpc.ContactsServiceServicer):
    _default_page_size = 20

    def __init__(
        self,
        contacts: repositories.ContactsRepository,
        companies: repositories.CompaniesRepository,
    ):
        self._contacts = contacts
        self._companies = companies

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["ContactsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_ContactsServiceServicer_to_server(self, server)

    async def CreateContact(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateContactRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateContactResponse:
        company = await self._companies.find_by_id(request.contact.company_id)

        if not company:
            return await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Company not found",
                trailing_metadata=(
                    ("field_name", "company_id"),
                    ("field_description", "Company is not found"),
                ),
            )

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
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetContactResponse(contact=contact)

    async def ListCompanyContacts(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListCompanyContactsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListCompanyContactsResponse:
        contacts = await self._contacts.find_by_company_id(
            company_id=request.company_id,
            cursor=request.page_token,
            limit=request.page_size or self._default_page_size,
        )

        return grpc_pb2.ListCompanyContactsResponse(
            contacts=[contact async for contact in contacts],
            next_page_token=await contacts.cursor(),
        )

    async def UpdateContactReference(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateContactReferenceRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateContactReferenceResponse:
        contact = await self._contacts.find_by_id(request.contact_id)

        if not contact:
            return await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Contact not found",
                trailing_metadata=(
                    ("field_name", "contact_id"),
                    ("field_description", "Contact is not found"),
                ),
            )

        contact.external_reference = request.external_reference

        await self._contacts.update_reference(contact)

        return grpc_pb2.UpdateContactReferenceResponse(contact=contact)
